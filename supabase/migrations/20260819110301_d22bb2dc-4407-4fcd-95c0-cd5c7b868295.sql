CREATE TABLE public.post_comments (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  post_slug TEXT NOT NULL,
  display_name TEXT NOT NULL DEFAULT 'Anonymous',
  body TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  CONSTRAINT post_comments_body_len CHECK (char_length(btrim(body)) BETWEEN 2 AND 1000),
  CONSTRAINT post_comments_name_len CHECK (char_length(btrim(display_name)) BETWEEN 1 AND 40),
  CONSTRAINT post_comments_slug_len CHECK (char_length(post_slug) BETWEEN 1 AND 200)
);

CREATE INDEX post_comments_slug_created_idx ON public.post_comments (post_slug, created_at DESC);

GRANT SELECT, INSERT ON public.post_comments TO anon;
GRANT SELECT, INSERT ON public.post_comments TO authenticated;
GRANT ALL ON public.post_comments TO service_role;

ALTER TABLE public.post_comments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read comments"
  ON public.post_comments FOR SELECT
  TO anon, authenticated
  USING (true);

CREATE POLICY "Anyone can post a comment"
  ON public.post_comments FOR INSERT
  TO anon, authenticated
  WITH CHECK (true);