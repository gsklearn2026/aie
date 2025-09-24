FROM postgres:15-alpine

# Install curl for health checks
RUN apk add --no-cache curl

# Copy initialization scripts
COPY init/ /docker-entrypoint-initdb.d/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pg_isready -U ${POSTGRES_USER:-postgres} || exit 1

# Expose port
EXPOSE 5432
