# Notes App

A modern, secure notes-taking web application where each note is accessible via a unique URL with optional password protection. This app operates in fully anonymous mode - no login required!

## Features

- 🔗 **Unique URLs** - Each note gets its own memorable URL (e.g., `/note/my-ideas`)
- 🔒 **Password Protection** - Secure sensitive notes with optional passwords
- ✏️ **Live Editing** - Edit notes with auto-save functionality (saves after 1 second of inactivity)
- 🌐 **Fully Anonymous** - Create and share notes without any login or registration
- 📱 **Responsive Design** - Works seamlessly on desktop and mobile devices
- 🎨 **Modern UI** - Built with shadcn/ui and Tailwind CSS

## Tech Stack

### Frontend
- React 19
- TypeScript
- Tailwind CSS 4
- shadcn/ui components
- tRPC for type-safe API calls
- Wouter for routing

### Backend
- Node.js
- Express 4
- tRPC 11
- MySQL/TiDB database
- Drizzle ORM
- bcryptjs for password hashing

## Getting Started

### Prerequisites

- Node.js 22+
- MySQL or TiDB database
- pnpm package manager

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd notes-app
```

2. Install dependencies:
```bash
pnpm install
```

3. Set up environment variables:

Create a `.env` file in the root directory with the following:

```env
# Database
DATABASE_URL=mysql://user:password@host:port/database

# Security
JWT_SECRET=your-secret-key

# App Configuration (optional)
VITE_APP_ID=proj_abc123def456
VITE_APP_TITLE="Notes App"
VITE_APP_LOGO="https://placehold.co/40x40/3b82f6/ffffff?text=N"

# Infrastructure
PORT=3000
```

4. Run database migrations:
```bash
pnpm db:migrate
```

5. Start the development server:
```bash
pnpm dev
```

The application will be available at `http://localhost:3000`

## Database Schema

### Notes Table
- `id` - Unique note identifier (UUID)
- `slug` - URL-friendly unique identifier
- `title` - Note title
- `content` - Note content (Markdown)
- `password` - Optional bcrypt hashed password
- `userId` - Optional user ID (for future multi-user support)
- `createdAt` - Creation timestamp
- `updatedAt` - Last update timestamp

## API Endpoints (tRPC)

### Notes
- `notes.create` - Create a new note (public access)
- `notes.getBySlug` - Get note by slug (public access, content hidden if password-protected)
- `notes.verifyPassword` - Verify note password and access content

## Features in Detail

### Unique URL System
Each note is assigned a unique slug that becomes part of its URL. Users can choose custom slugs when creating notes, making them easy to remember and share.

### Password Protection
Notes can be optionally protected with a password. When a password is set:
- The note title and metadata are publicly visible
- The content is hidden until the correct password is provided
- Passwords are securely hashed using bcryptjs

### Anonymous Mode
The app operates in fully anonymous mode:
- No user registration or login required
- Anyone can create, view, and share notes
- Notes are accessible via their unique URLs
- Optional password protection provides content security

### Responsive Design
The application is built mobile-first and works seamlessly across all device sizes:
- Adaptive layouts for phone, tablet, and desktop
- Touch-friendly controls
- Optimized for both portrait and landscape orientations

## Development

### Available Scripts

- `pnpm dev` - Start development server
- `pnpm build` - Build for production
- `pnpm preview` - Preview production build
- `pnpm db:migrate` - Run database migrations
- `pnpm db:generate` - Generate migration files
- `pnpm db:studio` - Open Drizzle Studio for database management

## Security

- Password-protected notes use bcrypt hashing
- SQL injection protection via Drizzle ORM
- Environment variables for sensitive configuration
- HTTPS recommended for production deployment

## License

MIT
