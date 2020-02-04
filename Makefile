deploy:
	@ssh -i ${SSH_KEYFILE} -o "StrictHostKeyChecking=no" -t ubuntu@teststaging.somethingtechie.com "(\
          export DB_NAME=${DB_NAME};\
          export DB_PASS=${DB_PASS};\
          export DB_SERVICE=${DB_SERVICE};\
          export DB_PORT=${DB_PORT};\
          export DB_USER=${DB_USER};\
          export SECRET_KEY=${SECRET_KEY};\
          export SLACK_PASSWORD=${SLACK_PASSWORD};\
          export SLACK_EMAIL=${SLACK_EMAIL};\
          export SLACK_TOKEN=${SLACK_TOKEN};\
          export SLACK_WORKSPACE_URL=${SLACK_WORKSPACE_URL};\
          export BUILD_TAG=${BUILD_TAG};\
          export SENTRY_DSN=${SENTRY_DSN};\
          docker stack deploy -c /home/ubuntu/stacks/${BUILD_TAG} ${BUILD_TAG});\
          docker system prune -f"
