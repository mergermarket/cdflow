FROM ruby

RUN mkdir -p /usr/local/app/
WORKDIR /usr/local/app/

COPY Gemfile Gemfile.lock /usr/local/app/
RUN bundle install
