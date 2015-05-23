require 'open-uri'
require 'nokogiri'
require 'json'

class DailyNews < ActiveRecord::Base
  validates :content, presence: true

  scope :search, lambda { |query|
    news_list = reverse_sorted.where(['content LIKE ?', "%#{query}%"])

    if news_list.empty?
      return ""
    end

    result_list = []
    news_list.each do |news|
      JSON.parse(news.content).each do |single_news|
        if single_news['dailyTitle'].include? query
            found_news = {"date" => news['date'], "content" => single_news}
            result_list.push found_news
            next
          end

        if single_news['isMulti']
          single_news['questionTitleList'].each do |t|
            if t.include? query
              found_news = {"date" => news['date'], "content" => single_news}
              result_list.push found_news
              break
            end
          end
        else
          if single_news['questionTitle'].include? query
            found_news = {"date" => news['date'], "content" => single_news}
            result_list.push found_news
            next
          end
        end
      end
    end

    if result_list.empty?
      return ""
    end

    return result_list.to_json
  }

  scope :sorted, lambda { order('date ASC') }

  scope :reverse_sorted, lambda { order('date DESC') }

  def self.download_content(date_string)
    news_list = []

    JSON.parse(RestClient.get("http://news-at.zhihu.com/api/3/news/before/#{date_string}"))['stories'].each do |n|
        html_doc = Nokogiri::HTML(JSON.parse(RestClient.get("http://news-at.zhihu.com/api/3/news/#{n['id']}"))['body'])

        unless html_doc.at_css('div.view-more').nil?
          news = {}
          news['dailyTitle'] = n['title']
          news['thumbnailUrl'] = n['images'] == nil ? nil : n['images'][0]
          news['questionTitleList'] = []
          news['questionUrlList'] = []
          should_push = true

          if html_doc.css('div.view-more').size > 1
            news['isMulti'] = true

            html_doc.css('div.view-more').each do |element|
              if element.css('a').text != '查看知乎讨论'
                should_push = false
              end
              news['questionUrlList'].push(element.css('a').attr('href').to_s)
            end

            html_doc.css('h2').each do |element|
              title = element.text
              news['questionTitleList'].push(title == '' ? news['dailyTitle'] : title)
            end
          else
            news['isMulti'] = false
            title = html_doc.css('h2').text
            news['questionTitle'] = title == '' ? news['dailyTitle'] : title
            if html_doc.css('div.view-more').css('a').text == '查看知乎讨论'
              news['questionUrl'] = html_doc.css('div.view-more').css('a').attr('href').to_s
            else
              should_push = false
            end
          end

          if should_push
            news_list.push news
          end
        end
    end

    return news_list.to_json
  end
end
