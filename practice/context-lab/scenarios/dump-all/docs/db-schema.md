# Schema (excerpt)

users(id BIGINT pk, email TEXT unique, created_at TIMESTAMP)
pages(id BIGINT pk, url TEXT, fetched_at TIMESTAMP)
jobs(id BIGINT pk, kind TEXT, attempts INT)
