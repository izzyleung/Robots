class DailyNewsController < ApplicationController
  def raw
    @content = route_request(params[:date])
  end

  def search
    @result_list = DailyNews.search(params[:key_word])
  end

  private
  def date_after_today?(date_string)
    Time.zone.parse(date_string) > Time.zone.now
  end

  def date_before_birthday?(date_string)
    Time.zone.parse(date_string) <= Time.new(2013, 5, 19)
  end

  def route_request(date_string, option = {:method => :raw})
    begin
      time = Date.strptime(date_string, '%Y%m%d')
      @title = time.prev_day.strftime('%Y%m%d')
    rescue ArgumentError => e
      render :status => 404
    end

    if date_after_today?(date_string)
      DailyNews.sorted.last.content
    elsif date_before_birthday?(date_string)
      render :status => 404
    else
      queryed_daily_news = DailyNews.find_by_date(date_string)
      if queryed_daily_news
        queryed_daily_news.content
      else
        queryed_daily_news = DailyNews.new
        queryed_daily_news.date = date_string
        queryed_daily_news.content = DailyNews.download_content(date_string)
        unless queryed_daily_news.save
          render :status => 404
        end
        queryed_daily_news.content
      end
    end
  end
end
