source "https://rubygems.org"
ruby "~> 3.4.0"

gem "jekyll", "~> 4.4"
gem "minimal-mistakes-jekyll", "4.28.1"
gem "webrick", "~> 1.9"
gem "tzinfo-data", platforms: [:windows, :jruby]

group :jekyll_plugins do
  gem "jekyll-paginate", "~> 1.1"
  gem "jekyll-sitemap", "~> 1.4"
  gem "jekyll-gist", "~> 1.5"
  gem "jekyll-feed", "~> 0.17"
  gem "jemoji", "~> 0.13"
  gem "jekyll-include-cache", "~> 0.2"
end

# Native file watching on BSD
if RbConfig::CONFIG['target_os'] =~ /(?i-mx:bsd|dragonfly)/
  gem 'rb-kqueue', '>= 0.2'
end
