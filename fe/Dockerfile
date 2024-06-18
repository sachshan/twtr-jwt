###########
# BUILDER #
###########

# pull official base image
FROM public.ecr.aws/docker/library/node:15.2.0-alpine as builder

# set working directory
WORKDIR /usr/src/app

# add /usr/src/app/node_modules/.bin to $PATH
ENV PATH /usr/src/app/node_modules/.bin:$PATH

# install and cache app dependencies
COPY package.json .
COPY package-lock.json .
RUN npm ci
#RUN npm install react-scripts@4.0.0 --silent

# set environment variables
ARG REACT_APP_API_SERVICE_URL
ENV REACT_APP_API_SERVICE_URL $REACT_APP_API_SERVICE_URL
ARG NODE_ENV
ENV NODE_ENV $NODE_ENV

# create build
COPY . .
RUN npm run build

#########
# FINAL #
#########

# base image
FROM public.ecr.aws/docker/library/nginx:stable-perl

# update nginx conf
#RUN rm -rf /etc/nginx/conf.d
#COPY conf /etc/nginx

# copy static files
COPY --from=builder /usr/src/app/build /usr/share/nginx/html

# expose port
EXPOSE 80

# run nginx
# Nginx uses the daemon off directive to run in the foreground. 
# This makes it easy to run in debug mode (foreground) and directly switch 
# to running in production mode (background) by changing command line args.
# But, as of 22 October 2019, official Nginx docker images all have line:
#CMD ["nginx", "-g", "daemon off;"]
# So, don't need to specify it in our Dockerfile.