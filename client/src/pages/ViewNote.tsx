import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { trpc } from "@/lib/trpc";
import { useState } from "react";
import { useLocation, useRoute } from "wouter";
import { toast } from "sonner";
import { Lock } from "lucide-react";

export default function ViewNote() {
  const [, params] = useRoute("/note/:slug");
  const [, setLocation] = useLocation();
  const slug = params?.slug || "";
  
  const [password, setPassword] = useState("");
  const [unlockedContent, setUnlockedContent] = useState<string | null>(null);

  const { data: note, isLoading, error } = trpc.notes.getBySlug.useQuery(
    { slug },
    { enabled: !!slug }
  );

  const verifyMutation = trpc.notes.verifyPassword.useMutation({
    onSuccess: (data) => {
      setUnlockedContent(data.content);
      toast.success("Password correct!");
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!password.trim()) {
      toast.error("Please enter a password");
      return;
    }
    verifyMutation.mutate({ slug, password });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-muted-foreground">Loading note...</p>
      </div>
    );
  }

  if (error || !note) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Note Not Found</CardTitle>
            <CardDescription>The note you're looking for doesn't exist</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => setLocation("/")} className="w-full">
              Go Home
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const displayContent = unlockedContent || note.content;
  const isLocked = note.hasPassword && !unlockedContent;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-4 py-12">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <Button variant="ghost" onClick={() => setLocation("/")}>
            ← Back to Home
          </Button>
        </div>

        <Card>
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <CardTitle className="text-3xl mb-2">{note.title}</CardTitle>
                <CardDescription>
                  Created: {note.createdAt ? new Date(note.createdAt).toLocaleDateString() : "Unknown"}
                  {note.hasPassword && (
                    <span className="ml-3 inline-flex items-center gap-1 text-amber-600">
                      <Lock className="w-3 h-3" />
                      Password Protected
                    </span>
                  )}
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {isLocked ? (
              <div className="space-y-6">
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-6 text-center">
                  <Lock className="w-12 h-12 text-amber-600 mx-auto mb-3" />
                  <h3 className="text-lg font-semibold text-amber-900 mb-2">This note is password protected</h3>
                  <p className="text-amber-700 text-sm">Enter the password to view the content</p>
                </div>

                <form onSubmit={handlePasswordSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="password">Password</Label>
                    <Input
                      id="password"
                      type="password"
                      placeholder="Enter password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                    />
                  </div>
                  <Button type="submit" disabled={verifyMutation.isPending} className="w-full">
                    {verifyMutation.isPending ? "Verifying..." : "Unlock Note"}
                  </Button>
                </form>
              </div>
            ) : (
              <div className="prose prose-slate max-w-none">
                <div className="whitespace-pre-wrap text-slate-700 leading-relaxed">
                  {displayContent || <em className="text-slate-400">No content</em>}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

