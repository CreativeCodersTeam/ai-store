---
name: create-spring-boot-java-project
description: Scaffolds a new Spring Boot Java project from Spring Initializr with PostgreSQL, Redis, MongoDB, Docker Compose, and OpenAPI/Swagger support. Use when asked to create a new Java project, bootstrap a Spring Boot app, generate a project skeleton, or set up a Java microservice from scratch.
---

# Create Spring Boot Java Project

## Prerequisites

- Latest Java LTS or newer
- Docker and Docker Compose

To customize the project name, change `artifactId` and `packageName` in the download step.

> **Versions:** Always use the latest stable versions for Java LTS, Spring Boot, springdoc, archunit, and Docker images unless the user explicitly requests specific versions. Verify current versions on [Maven Central](https://central.sonatype.com/) before scaffolding.

## Step 1: Check Java version

```shell
java -version
```

## Step 2: Download and extract Spring Boot template

```shell
curl https://start.spring.io/starter.zip \
  -d artifactId=${input:projectName:demo-java} \
  -d bootVersion=${input:bootVersion:LATEST_STABLE} \
  -d dependencies=lombok,configuration-processor,web,data-jpa,postgresql,data-redis,data-mongodb,validation,cache,testcontainers \
  -d javaVersion=${input:javaVersion:LATEST_LTS} \
  -d packageName=com.example \
  -d packaging=jar \
  -d type=maven-project \
  -o starter.zip
unzip starter.zip -d ./${input:projectName:demo-java}
rm -f starter.zip
cd ${input:projectName:demo-java}
```

## Step 3: Add additional dependencies

Insert into `pom.xml`:

```xml
<dependency>
  <groupId>org.springdoc</groupId>
  <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
  <version>LATEST_STABLE</version>
</dependency>
<dependency>
  <groupId>com.tngtech.archunit</groupId>
  <artifactId>archunit-junit5</artifactId>
  <version>LATEST_STABLE</version>
  <scope>test</scope>
</dependency>
```

## Step 4: Configure application.properties

Add the following configurations:

```properties
# SpringDoc
springdoc.swagger-ui.doc-expansion=none
springdoc.swagger-ui.operations-sorter=alpha
springdoc.swagger-ui.tags-sorter=alpha

# Redis
spring.data.redis.host=localhost
spring.data.redis.port=6379
spring.data.redis.password=${REDIS_PASSWORD:changeme}

# JPA / PostgreSQL
spring.datasource.driver-class-name=org.postgresql.Driver
spring.datasource.url=jdbc:postgresql://localhost:5432/postgres
spring.datasource.username=postgres
spring.datasource.password=${DB_PASSWORD:changeme}
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true

# MongoDB
spring.data.mongodb.host=localhost
spring.data.mongodb.port=27017
spring.data.mongodb.authentication-database=admin
spring.data.mongodb.username=root
spring.data.mongodb.password=${MONGO_PASSWORD:changeme}
spring.data.mongodb.database=test
```

## Step 5: Create docker-compose.yaml

Create `docker-compose.yaml` at project root with these services:

| Service | Image | Port | Volume | Auth |
|---------|-------|------|--------|------|
| redis | redis:LATEST_STABLE | 6379:6379 | `./redis_data:/data` | password: `rootroot` |
| postgresql | postgresql:LATEST_STABLE | 5432:5432 | `./postgres_data:/var/lib/postgresql/data` | password: `rootroot` |
| mongo | mongo:LATEST_STABLE | 27017:27017 | `./mongo_data:/data/db` | root/`rootroot` |

## Step 6: Update .gitignore

Add `redis_data`, `postgres_data`, and `mongo_data` directories.

## Step 7: Verify

```shell
./mvnw clean test
```

Optional: `docker-compose up -d` to start services, `./mvnw spring-boot:run` to run the app, `docker-compose rm -sf` to stop.

## Let's do this step by step
