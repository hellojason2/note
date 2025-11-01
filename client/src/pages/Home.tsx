import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { APP_TITLE, getLoginUrl } from "@/const";
import { useLocation } from "wouter";
import { FileText, Lock, Link2, Zap } from "lucide-react";

export default function Home() {
  const { isAuthenticated, loading, logout } = useAuth();
  const [, setLocation] = useLocation();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-slate-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <FileText className="w-6 h-6 text-blue-600" />
            <h1 className="text-xl font-bold text-slate-900">{APP_TITLE}</h1>
          </div>
          <nav className="flex items-center gap-3">
            {loading ? (
              <span className="text-sm text-muted-foreground">Loading...</span>
            ) : isAuthenticated ? (
              <>
                <Button variant="ghost" onClick={() => setLocation("/my-notes")}>
                  My Notes
                </Button>
                <Button onClick={() => setLocation("/create")}>Create Note</Button>
                <Button variant="outline" onClick={() => logout()}>
                  Logout
                </Button>
              </>
            ) : (
              <Button asChild>
                <a href={getLoginUrl()}>Login</a>
              </Button>
            )}
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 text-center">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-5xl font-bold text-slate-900 mb-6">
            Share Notes with
            <span className="text-blue-600"> Unique Links</span>
          </h2>
          <p className="text-xl text-slate-600 mb-8">
            Create notes that are accessible via memorable URLs. Add password protection to keep your content secure.
          </p>
          <div className="flex gap-4 justify-center">
            <Button size="lg" onClick={() => setLocation("/create")}>
              Create Your First Note
            </Button>
            {isAuthenticated && (
              <Button size="lg" variant="outline" onClick={() => setLocation("/my-notes")}>
                View My Notes
              </Button>
            )}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
          <Card>
            <CardHeader>
              <Link2 className="w-10 h-10 text-blue-600 mb-2" />
              <CardTitle>Unique URLs</CardTitle>
              <CardDescription>
                Each note gets its own memorable URL that you can share with anyone
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-600">
                Create custom slugs like <span className="font-mono bg-slate-100 px-1 rounded">/my-ideas</span> for easy sharing
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Lock className="w-10 h-10 text-amber-600 mb-2" />
              <CardTitle>Password Protection</CardTitle>
              <CardDescription>
                Secure your sensitive notes with optional password protection
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-600">
                Only people with the password can view protected notes
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Zap className="w-10 h-10 text-green-600 mb-2" />
              <CardTitle>Quick & Simple</CardTitle>
              <CardDescription>
                No complicated setup. Just write and share instantly
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-600">
                Create, manage, and share your notes in seconds
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* CTA Section */}
      <section className="container mx-auto px-4 py-16">
        <Card className="max-w-3xl mx-auto bg-gradient-to-br from-blue-600 to-blue-700 text-white border-0">
          <CardHeader className="text-center">
            <CardTitle className="text-3xl text-white mb-2">Ready to get started?</CardTitle>
            <CardDescription className="text-blue-100">
              Create your first note and share it with the world
            </CardDescription>
          </CardHeader>
          <CardContent className="flex justify-center">
            {isAuthenticated ? (
              <Button size="lg" variant="secondary" onClick={() => setLocation("/create")}>
                Create a Note Now
              </Button>
            ) : (
              <Button size="lg" variant="secondary" asChild>
                <a href={getLoginUrl()}>Login to Start</a>
              </Button>
            )}
          </CardContent>
        </Card>
      </section>

      {/* Footer */}
      <footer className="border-t bg-slate-50 mt-20">
        <div className="container mx-auto px-4 py-8 text-center text-sm text-slate-600">
          <p>© 2024 {APP_TITLE}. Simple note sharing made easy.</p>
        </div>
      </footer>
    </div>
  );
}
