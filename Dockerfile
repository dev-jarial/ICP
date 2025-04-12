FROM postgres:latest

# Install dependencies for building extensions
RUN apt-get update && apt-get install -y \
    postgresql-server-dev-all \
    build-essential \
    git

# Install PGVector extension
RUN git clone https://github.com/pgvector/pgvector.git /tmp/pgvector && \
    cd /tmp/pgvector && \
    make && \
    make install && \
    rm -rf /tmp/pgvector

# Clean up apt cache
RUN apt-get clean
