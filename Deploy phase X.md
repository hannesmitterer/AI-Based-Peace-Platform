name: Deploy Phase X

on:
  push:
    branches: [ main ]

jobs:
  build-test-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: npm ci
      - name: Run unit & integration tests
        run: npm test
      - name: Deploy to production
        if: success()
        run: npm run deploy
