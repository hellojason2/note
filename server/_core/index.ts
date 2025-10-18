import "dotenv/config";
import express from "express";
import { createServer } from "http";
import net from "net";
import { createExpressMiddleware } from "@trpc/server/adapters/express";
import { appRouter } from "../routers";
import { createContext } from "./context";
import { serveStatic, setupVite } from "./vite";
import { drizzle } from "drizzle-orm/mysql2";
import { migrate } from "drizzle-orm/mysql2/migrator";
import mysql from "mysql2/promise";

function isPortAvailable(port: number): Promise<boolean> {
  return new Promise(resolve => {
    const server = net.createServer();
    server.listen(port, () => {
      server.close(() => resolve(true));
    });
    server.on("error", () => resolve(false));
  });
}

async function findAvailablePort(startPort: number = 3000): Promise<number> {
  for (let port = startPort; port < startPort + 20; port++) {
    if (await isPortAvailable(port)) {
      return port;
    }
  }
  throw new Error(`No available port found starting from ${startPort}`);
}

async function runMigrations() {
  try {
    console.log("Running database migrations...");
    const connectionString = process.env.DATABASE_URL;
    if (!connectionString) {
      throw new Error("DATABASE_URL environment variable is not set");
    }

    const connection = await mysql.createConnection(connectionString);
    const db = drizzle(connection);
    await migrate(db, { migrationsFolder: "./migrations" });
    console.log("Migrations completed successfully");
    await connection.end();
  } catch (error) {
    console.error("Migration failed:", error);
    throw error;
  }
}

async function start() {
  const app = express();
  const server = createServer(app);
  
  // Run migrations first
  await runMigrations();

  // tRPC middleware
  app.use(
    "/api/trpc",
    createExpressMiddleware({
      router: appRouter,
      createContext,
    })
  );

  // Vite middleware or static files
  if (process.env.NODE_ENV === "development") {
    await setupVite(app, server);
  } else {
    serveStatic(app);
  }

  const port = await findAvailablePort();
  server.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
  });
}

start().catch(console.error);
