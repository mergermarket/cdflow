FROM ruby

RUN mkdir /usr/local/app/
WORKDIR /usr/local/app/

COPY Gemfile Gemfile.lock /usr/local/app/
RUN gem install bundler && bundle
