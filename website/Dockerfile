FROM jekyll/jekyll:4.2.2
WORKDIR /srv/jekyll
COPY ./ ./
RUN mkdir -p /home/static
#RUN bundle install --jobs 20 --retry 5
RUN bundle update --bundler
CMD bundle exec jekyll build  

