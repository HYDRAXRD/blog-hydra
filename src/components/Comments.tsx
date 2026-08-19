import { useEffect, useState } from "react";
import { MessageCircle, Send, Loader2 } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";

interface Comment {
  id: string;
  display_name: string;
  body: string;
  created_at: string;
}

const formatWhen = (iso: string): string =>
  new Date(iso).toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

export default function Comments({ slug }: { slug: string }) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState("");
  const [body, setBody] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    supabase
      .from("post_comments")
      .select("id, display_name, body, created_at")
      .eq("post_slug", slug)
      .order("created_at", { ascending: false })
      .limit(200)
      .then(({ data, error: err }) => {
        if (!active) return;
        if (err) setError("Couldn't load comments.");
        setComments((data as Comment[] | null) ?? []);
        setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [slug]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    const text = body.trim();
    if (text.length < 2) {
      setError("Write at least a couple of characters.");
      return;
    }
    setSending(true);
    setError(null);

    const { data, error: err } = await supabase
      .from("post_comments")
      .insert({
        post_slug: slug,
        display_name: name.trim() || "Anonymous",
        body: text,
      })
      .select("id, display_name, body, created_at")
      .single();

    setSending(false);
    if (err || !data) {
      setError("Couldn't post your comment. Try again.");
      return;
    }
    setComments((prev) => [data as Comment, ...prev]);
    setBody("");
  };

  return (
    <section className="mt-14 border-t border-border/50 pt-10">
      <h2 className="flex items-center gap-2 font-display text-xl font-bold">
        <MessageCircle size={18} className="text-primary" />
        Comments
        <span className="text-sm font-normal text-muted-foreground">({comments.length})</span>
      </h2>
      <p className="mt-1 text-xs text-muted-foreground">
        No account needed — leave your take anonymously.
      </p>

      <form onSubmit={submit} className="mt-6 space-y-3">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          maxLength={40}
          placeholder="Name (optional) — defaults to Anonymous"
          className="w-full rounded-lg border border-border/60 bg-card/60 px-4 py-2.5 text-sm text-foreground outline-none transition-colors placeholder:text-muted-foreground focus:border-primary/60"
        />
        <textarea
          value={body}
          onChange={(e) => setBody(e.target.value)}
          maxLength={1000}
          rows={4}
          placeholder="Share your thoughts on this call…"
          className="w-full resize-y rounded-lg border border-border/60 bg-card/60 px-4 py-3 text-sm text-foreground outline-none transition-colors placeholder:text-muted-foreground focus:border-primary/60"
        />
        <div className="flex items-center justify-between gap-4">
          <span className="text-xs text-muted-foreground">{body.length}/1000</span>
          <button
            type="submit"
            disabled={sending}
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-bold text-primary-foreground transition-opacity hover:opacity-90 disabled:opacity-50"
          >
            {sending ? <Loader2 size={15} className="animate-spin" /> : <Send size={15} />}
            Post comment
          </button>
        </div>
        {error && <p className="text-xs text-destructive">{error}</p>}
      </form>

      <div className="mt-8 space-y-4">
        {loading && <p className="text-sm text-muted-foreground">Loading comments…</p>}
        {!loading && comments.length === 0 && (
          <p className="text-sm text-muted-foreground">
            No comments yet. Be the first to speak up.
          </p>
        )}
        {comments.map((c) => (
          <article
            key={c.id}
            className="rounded-xl border border-border/60 bg-card/50 p-4 transition-colors hover:border-primary/40"
          >
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className="font-display font-bold text-primary">{c.display_name}</span>
              <span className="opacity-40">•</span>
              <span className="text-muted-foreground">{formatWhen(c.created_at)}</span>
            </div>
            <p className="mt-2 text-sm leading-relaxed whitespace-pre-wrap text-foreground/90">
              {c.body}
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}
