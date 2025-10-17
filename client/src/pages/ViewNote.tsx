import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { trpc } from "@/lib/trpc";
import { useEffect, useState, useRef } from "react";
import { useLocation, useRoute } from "wouter";
import { toast } from "sonner";
import { Lock, Edit, Save, X } from "lucide-react";

export default function ViewNote() {
  const { user } = useAuth();
  const [, params] = useRoute("/note/:slug");
  const [, setLocation] = useLocation();
  const slug = params?.slug || "";
  
  const [password, setPassword] = useState("");
  const [unlockedContent, setUnlockedContent] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState("");
  const [editContent, setEditContent] = useState("");
  const [editPassword, setEditPassword] = useState("");
  const [hasPasswordChange, setHasPasswordChange] = useState(false);
  
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const utils = trpc.useUtils();

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

  const updateMutation = trpc.notes.update.useMutation({
    onSuccess: () => {
      toast.success("Note saved");
      utils.notes.getBySlug.invalidate({ slug });
    },
    onError: (error) => {
      toast.error(error.message);
    },
  });

  // Initialize edit fields when entering edit mode
  useEffect(() => {
    if (isEditing && note) {
      setEditTitle(note.title);
      setEditContent(unlockedContent || note.content || "");
      setEditPassword("");
      setHasPasswordChange(false);
    }
  }, [isEditing, note, unlockedContent]);

  // Auto-save with debounce
  useEffect(() => {
    if (!isEditing || !note) return;

    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }

    saveTimeoutRef.current = setTimeout(() => {
      const updateData: {
        id: string;
        title?: string;
        content?: string;
        password?: string | null;
      } = {
        id: note.id,
        title: editTitle,
        content: editContent,
      };

      // Only include password if user explicitly changed it
      if (hasPasswordChange) {
        updateData.password = editPassword.trim() || null;
      }

      updateMutation.mutate(updateData);
    }, 1000); // Auto-save after 1 second of inactivity

    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, [editTitle, editContent, editPassword, hasPasswordChange, isEditing, note]);

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!password.trim()) {
      toast.error("Please enter a password");
      return;
    }
    verifyMutation.mutate({ slug, password });
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }
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
  const isOwner = user?.id === note.userId;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-4 py-12">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6 flex items-center justify-between">
          <Button variant="ghost" onClick={() => setLocation("/")}>
            ← Back to Home
          </Button>
          {isOwner && !isLocked && !isEditing && (
            <Button onClick={() => setIsEditing(true)}>
              <Edit className="w-4 h-4 mr-2" />
              Edit Note
            </Button>
          )}
          {isEditing && (
            <Button variant="outline" onClick={handleCancelEdit}>
              <X className="w-4 h-4 mr-2" />
              Cancel
            </Button>
          )}
        </div>

        <Card>
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                {isEditing ? (
                  <div className="space-y-3">
                    <div>
                      <Label htmlFor="edit-title">Title</Label>
                      <Input
                        id="edit-title"
                        value={editTitle}
                        onChange={(e) => setEditTitle(e.target.value)}
                        className="text-2xl font-bold"
                      />
                    </div>
                    <div className="text-sm text-muted-foreground">
                      Auto-saving... {updateMutation.isPending && <span className="text-blue-600">Saving...</span>}
                    </div>
                  </div>
                ) : (
                  <>
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
                  </>
                )}
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
            ) : isEditing ? (
              <div className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="edit-content">Content</Label>
                  <Textarea
                    id="edit-content"
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    rows={15}
                    className="resize-y font-mono"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="edit-password">Change Password (Optional)</Label>
                  <Input
                    id="edit-password"
                    type="password"
                    placeholder="Leave empty to keep current password, or enter new password"
                    value={editPassword}
                    onChange={(e) => {
                      setEditPassword(e.target.value);
                      setHasPasswordChange(true);
                    }}
                  />
                  <p className="text-xs text-muted-foreground">
                    {note.hasPassword 
                      ? "Currently password protected. Enter a new password to change it, or leave empty to keep the current one."
                      : "Enter a password to protect this note, or leave empty to keep it public."}
                  </p>
                </div>

                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Save className="w-4 h-4" />
                  <span>Changes are automatically saved as you type</span>
                </div>
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

