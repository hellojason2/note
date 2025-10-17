# Notes App

A modern, secure notes-taking web application where each note is accessible via a unique URL with optional password protection.

## Features

- 🔗 **Unique URLs** - Each note gets its own memorable URL (e.g., `/note/my-ideas`)
- 🔒 **Password Protection** - Secure sensitive notes with optional passwords
- ✏️ **Live Editing** - Edit notes with auto-save functionality (saves after 1 second of inactivity)
- 👤 **User Authentication** - Secure login via Manus OAuth
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

# Authentication
JWT_SECRET=your-secret-key
VITE_APP_ID=your-app-id
OAUTH_SERVER_URL=https://api.manus.im
VITE_OAUTH_PORTAL_URL=https://oauth.manus.im

# App Configuration
VITE_APP_TITLE=Notes App
VITE_APP_LOGO=https://your-logo-url.com/logo.png

# Owner (Optional)
OWNER_OPEN_ID=owner-id
OWNER_NAME=Owner Name
```

4. Push database schema:
```bash
pnpm db:push
```

5. Start the development server:
```bash
pnpm dev
```

The app will be available at `http://localhost:3000`

## Database Schema

### Users Table
- `id` - User ID (primary key)
- `name` - User name
- `email` - User email
- `loginMethod` - Authentication method
- `role` - User role (user/admin)
- `createdAt` - Account creation timestamp
- `lastSignedIn` - Last sign-in timestamp

### Notes Table
- `id` - Note ID (primary key)
- `slug` - Unique URL slug
- `title` - Note title
- `content` - Note content
- `password` - Hashed password (optional)
- `userId` - Owner user ID
- `createdAt` - Creation timestamp
- `updatedAt` - Last update timestamp

## API Endpoints (tRPC)

### Authentication
- `auth.me` - Get current user
- `auth.logout` - Logout user

### Notes
- `notes.create` - Create a new note
- `notes.getBySlug` - Get note by slug (public)
- `notes.verifyPassword` - Verify password and unlock note
- `notes.myNotes` - List all user's notes
- `notes.update` - Update note (owner only)
- `notes.delete` - Delete note (owner only)

## Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Import project to Vercel
3. Configure environment variables
4. Deploy

### Manual Deployment

1. Build the project:
```bash
pnpm build
```

2. Start production server:
```bash
pnpm start
```

## Project Structure

```
notes-app/
├── client/              # Frontend React app
│   ├── src/
│   │   ├── pages/      # Page components
│   │   ├── components/ # Reusable UI components
│   │   ├── lib/        # tRPC client setup
│   │   └── App.tsx     # Main app component
├── server/             # Backend Express app
│   ├── routers.ts      # tRPC routes
│   ├── db.ts           # Database queries
│   └── _core/          # Core server utilities
├── drizzle/            # Database schema & migrations
│   └── schema.ts       # Database schema definition
└── shared/             # Shared types & constants
```

## Features in Detail

### Note Creation
- Custom URL slugs or auto-generated random slugs
- Rich text content area
- Optional password protection

### Note Viewing
- Public access to unprotected notes
- Password prompt for protected notes
- Clean, readable interface

### Note Editing
- Only available to note owners
- Auto-save after 1 second of inactivity
- Edit title, content, and password
- Visual feedback for save status

### Security
- Passwords hashed with bcryptjs
- User authentication required for creating/editing
- Owner-only access control for modifications

## License

MIT

## Support

For issues or questions, please open an issue on GitHub.

