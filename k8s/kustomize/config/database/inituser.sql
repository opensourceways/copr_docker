DO
$$
BEGIN
  IF NOT EXISTS (SELECT * FROM pg_user WHERE usename = 'resalloc') THEN
     CREATE USER resalloc WITH PASSWORD 'resallocpass';
  END IF;
END
$$;
