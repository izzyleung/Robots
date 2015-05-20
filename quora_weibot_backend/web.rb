%W{sinatra twitter json ./credential.rb}.each(&method(:require))

set :server, 'webrick'
set :environment, :production

client = Twitter::REST::Client.new do |config|
  config.consumer_key = Credential::CONSUMER_KEY
  config.consumer_secret = Credential::CONSUMER_SECRET
  config.access_token = Credential::ACCESS_TOKEN
  config.access_token_secret = Credential::ACCESS_TOKEN_SECRET
end

get '/' do
  'How I wish, how I wish you were here.'
end

get '/timeline/:user' do |user|
  client.user_timeline(user, {count: params[:count] ||= 20}).map do |t|
    {
      twitter_id: t.id,
      status_text: t.text.dup.tap { |text| t.urls.each { |u| text.gsub!(u.attrs[:url], u.attrs[:expanded_url]) } },
      urls: t.urls.map { |u| u.expanded_url }
    }
  end.to_json
end
