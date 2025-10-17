import { eq } from "drizzle-orm";
import { drizzle } from "drizzle-orm/mysql2";
import { InsertUser, users } from "../drizzle/schema";
import { ENV } from './_core/env';

let _db: ReturnType<typeof drizzle> | null = null;

// Lazily create the drizzle instance so local tooling can run without a DB.
export async function getDb() {
  if (!_db && process.env.DATABASE_URL) {
    try {
      _db = drizzle(process.env.DATABASE_URL);
    } catch (error) {
      console.warn("[Database] Failed to connect:", error);
      _db = null;
    }
  }
  return _db;
}

export async function upsertUser(user: InsertUser): Promise<void> {
  if (!user.id) {
    throw new Error("User ID is required for upsert");
  }

  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot upsert user: database not available");
    return;
  }

  try {
    const values: InsertUser = {
      id: user.id,
    };
    const updateSet: Record<string, unknown> = {};

    const textFields = ["name", "email", "loginMethod"] as const;
    type TextField = (typeof textFields)[number];

    const assignNullable = (field: TextField) => {
      const value = user[field];
      if (value === undefined) return;
      const normalized = value ?? null;
      values[field] = normalized;
      updateSet[field] = normalized;
    };

    textFields.forEach(assignNullable);

    if (user.lastSignedIn !== undefined) {
      values.lastSignedIn = user.lastSignedIn;
      updateSet.lastSignedIn = user.lastSignedIn;
    }
    if (user.role === undefined) {
      if (user.id === ENV.ownerId) {
        user.role = 'admin';
        values.role = 'admin';
        updateSet.role = 'admin';
      }
    }

    if (Object.keys(updateSet).length === 0) {
      updateSet.lastSignedIn = new Date();
    }

    await db.insert(users).values(values).onDuplicateKeyUpdate({
      set: updateSet,
    });
  } catch (error) {
    console.error("[Database] Failed to upsert user:", error);
    throw error;
  }
}

export async function getUser(id: string) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot get user: database not available");
    return undefined;
  }

  const result = await db.select().from(users).where(eq(users.id, id)).limit(1);

  return result.length > 0 ? result[0] : undefined;
}

// Note operations
import { notes, InsertNote, Note } from "../drizzle/schema";
import { nanoid } from "nanoid";
import bcrypt from "bcryptjs";

export async function createNote(data: {
  slug: string;
  title: string;
  content: string;
  password?: string;
  userId: string;
}): Promise<Note> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const id = nanoid();
  const passwordHash = data.password ? await bcrypt.hash(data.password, 10) : null;

  const insertData: InsertNote = {
    id,
    slug: data.slug,
    title: data.title,
    content: data.content,
    password: passwordHash,
    userId: data.userId,
  };

  await db.insert(notes).values(insertData);
  const result = await db.select().from(notes).where(eq(notes.id, id)).limit(1);
  return result[0];
}

export async function getNoteBySlug(slug: string): Promise<Note | undefined> {
  const db = await getDb();
  if (!db) return undefined;

  const result = await db.select().from(notes).where(eq(notes.slug, slug)).limit(1);
  return result.length > 0 ? result[0] : undefined;
}

export async function getNotesByUserId(userId: string): Promise<Note[]> {
  const db = await getDb();
  if (!db) return [];

  return await db.select().from(notes).where(eq(notes.userId, userId));
}

export async function updateNote(
  id: string,
  data: {
    title?: string;
    content?: string;
    password?: string | null;
  }
): Promise<void> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  const updateData: Partial<InsertNote> = {};
  if (data.title !== undefined) updateData.title = data.title;
  if (data.content !== undefined) updateData.content = data.content;
  if (data.password !== undefined) {
    updateData.password = data.password ? await bcrypt.hash(data.password, 10) : null;
  }

  await db.update(notes).set(updateData).where(eq(notes.id, id));
}

export async function deleteNote(id: string): Promise<void> {
  const db = await getDb();
  if (!db) throw new Error("Database not available");

  await db.delete(notes).where(eq(notes.id, id));
}

export async function verifyNotePassword(note: Note, password: string): Promise<boolean> {
  if (!note.password) return true; // No password set
  return await bcrypt.compare(password, note.password);
}

export async function checkSlugExists(slug: string): Promise<boolean> {
  const db = await getDb();
  if (!db) return false;

  const result = await db.select().from(notes).where(eq(notes.slug, slug)).limit(1);
  return result.length > 0;
}
