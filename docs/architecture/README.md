Architecture overview

I started from the requirements, not the tech stack. I wrote down what the portal must do (search, listing pages, login, favourites, inquiries, agent listings) and how well it must do it (fast search, found on Google, scales on demand, secure, cheap to run). Each of those became a design rule, and each rule decided one part of the architecture.

Two examples. Listings must rank on Google, so public pages are server-rendered with Nuxt, and because SSR needs a Node server, the frontend runs on AWS Fargate rather than as static files. The app must scale by adding containers, so nothing is kept in server memory: login uses JWT, and Redis holds revoked tokens, rate limits and the search cache.

On AWS, traffic goes CloudFront → load balancer → FastAPI and Nuxt on Fargate, with MySQL (RDS) and Redis in private subnets that the internet cannot reach. Terraform builds the infrastructure, and GitHub Actions deploys it.

I drew each main flow (search, view listing, login, favourites, inquiry, listing lifecycle) as a sequence diagram, so every step and error case is visible before any code is written.