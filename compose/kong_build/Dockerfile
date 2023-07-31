FROM kong:2.3.3-alpine

LABEL description="Alpine + Kong 2.3.3 + kong-oidc plugin"

USER root
RUN apk update && apk add git unzip luarocks
RUN luarocks install kong-oidc
RUN luarocks install lua-resty-openidc 1.7.4 --force

#USER kong
