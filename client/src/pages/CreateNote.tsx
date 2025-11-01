import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { getLoginUrl } from "@/const";
import { trpc } from "@/lib/trpc";
import { useState } from "react";
import { useLocation } from "wouter";
import { toast } from "sonner";

export default function CreateNote() {
  const { isAuthenticated, loading } = useAuth();
  const [, setLocation] = useLocation();
  const [slug, setSlug] = useState("");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [password, setPassword] = useState("");

  const createMutation = trpc.notes.create.useMutation({
    onSuccess: (data) => {
      toast.success("Note created successfully!");
      setLocation(`/${data.slug}`);
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!slug.trim() || !title.trim()) {
      toast.error("Slug and title are required");
      return;
    }

    createMutation.mutate({
      slug: slug.trim(),
      title: title.trim(),
      content: content.trim(),
      password: password.trim() || undefined,
    });
  };

  const generateSlug = () => {
    const randomSlug = Math.random().toString(36).substring(2, 10);
    setSlug(randomSlug);
  };

  // Login is optional - users can create notes anonymously

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-4 py-12">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">Create a New Note</h1>
          <p className="text-slate-600">Share your thoughts with a unique, memorable URL</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Note Details</CardTitle>
            <CardDescription>Fill in the details below to create your note</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="slug">URL Slug *</Label>
                <div className="flex gap-2">
                  <Input
                    id="slug"
                    placeholder="my-awesome-note"
                    value={slug}
                    onChange={(e) => setSlug(e.target.value)}
                    required
                  />
                  <Button type="button" variant="outline" onClick={generateSlug}>
                    Generate
                  </Button>
                </div>
                <p className="text-sm text-muted-foreground">
                  Your note will be accessible at: <span className="font-mono">/{slug || "your-slug"}</span>
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="title">Title *</Label>
                <Input
                  id="title"
                  placeholder="Enter note title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="content">Content</Label>
                <Textarea
                  id="content"
                  placeholder="Write your note here..."
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  rows={10}
                  className="resize-y"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password (Optional)</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Leave empty for public note"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <p className="text-sm text-muted-foreground">
                  Add a password to protect your note from unauthorized access
                </p>
              </div>

              <div className="flex gap-3">
                <Button type="submit" disabled={createMutation.isPending} className="flex-1">
                  {createMutation.isPending ? "Creating..." : "Create Note"}
                </Button>
                <Button type="button" variant="outline" onClick={() => setLocation("/")}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

