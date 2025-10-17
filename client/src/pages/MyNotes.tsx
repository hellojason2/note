import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { getLoginUrl } from "@/const";
import { trpc } from "@/lib/trpc";
import { useLocation } from "wouter";
import { toast } from "sonner";
import { Lock, Trash2, ExternalLink } from "lucide-react";

export default function MyNotes() {
  const { isAuthenticated, loading } = useAuth();
  const [, setLocation] = useLocation();
  const utils = trpc.useUtils();

  const { data: notes, isLoading: notesLoading } = trpc.notes.myNotes.useQuery(undefined, {
    enabled: isAuthenticated,
  });

  const deleteMutation = trpc.notes.delete.useMutation({
    onSuccess: () => {
      toast.success("Note deleted successfully");
      utils.notes.myNotes.invalidate();
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  const handleDelete = (id: string, title: string) => {
    if (confirm(`Are you sure you want to delete "${title}"?`)) {
      deleteMutation.mutate({ id });
    }
  };

  if (loading || notesLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Login Required</CardTitle>
            <CardDescription>You need to login to view your notes</CardDescription>
          </CardHeader>
          <CardContent>
            <Button asChild className="w-full">
              <a href={getLoginUrl()}>Login</a>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-4 py-12">
      <div className="max-w-5xl mx-auto">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold text-slate-900 mb-2">My Notes</h1>
            <p className="text-slate-600">Manage all your created notes</p>
          </div>
          <div className="flex gap-3">
            <Button onClick={() => setLocation("/create")}>Create New Note</Button>
            <Button variant="outline" onClick={() => setLocation("/")}>
              Home
            </Button>
          </div>
        </div>

        {!notes || notes.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground mb-4">You haven't created any notes yet</p>
              <Button onClick={() => setLocation("/create")}>Create Your First Note</Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {notes.map((note) => (
              <Card key={note.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <CardTitle className="text-xl mb-1 truncate">{note.title}</CardTitle>
                      <CardDescription className="flex items-center gap-3 flex-wrap">
                        <span className="font-mono text-xs bg-slate-100 px-2 py-1 rounded">
                          /note/{note.slug}
                        </span>
                        {note.password && (
                          <span className="inline-flex items-center gap-1 text-amber-600 text-xs">
                            <Lock className="w-3 h-3" />
                            Protected
                          </span>
                        )}
                        <span className="text-xs">
                          Created: {note.createdAt ? new Date(note.createdAt).toLocaleDateString() : "Unknown"}
                        </span>
                      </CardDescription>
                    </div>
                    <div className="flex gap-2 flex-shrink-0">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setLocation(`/note/${note.slug}`)}
                      >
                        <ExternalLink className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => handleDelete(note.id, note.title)}
                        disabled={deleteMutation.isPending}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                {note.content && (
                  <CardContent>
                    <p className="text-sm text-slate-600 line-clamp-2">{note.content}</p>
                  </CardContent>
                )}
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

