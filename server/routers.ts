import { COOKIE_NAME } from "@shared/const";
import { getSessionCookieOptions } from "./_core/cookies";
import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, protectedProcedure, router } from "./_core/trpc";
import { TRPCError } from "@trpc/server";
import { z } from "zod";

export const appRouter = router({
  system: systemRouter,

  auth: router({
    me: publicProcedure.query(opts => opts.ctx.user),
    logout: publicProcedure.mutation(({ ctx }) => {
      const cookieOptions = getSessionCookieOptions(ctx.req);
      ctx.res.clearCookie(COOKIE_NAME, { ...cookieOptions, maxAge: -1 });
      return {
        success: true,
      } as const;
    }),
  }),

  notes: router({
    // Create a new note
    create: protectedProcedure
      .input(
        z.object({
          slug: z.string().min(1).max(255),
          title: z.string().min(1),
          content: z.string(),
          password: z.string().optional(),
        })
      )
      .mutation(async ({ ctx, input }) => {
        const { createNote, checkSlugExists } = await import("./db");
        
        // Check if slug already exists
        const exists = await checkSlugExists(input.slug);
        if (exists) {
          throw new TRPCError({
            code: "CONFLICT",
            message: "This URL slug is already taken. Please choose another.",
          });
        }

        return await createNote({
          slug: input.slug,
          title: input.title,
          content: input.content,
          password: input.password,
          userId: ctx.user.id,
        });
      }),

    // Get a note by slug (public access, but content hidden if password-protected)
    getBySlug: publicProcedure
      .input(z.object({ slug: z.string() }))
      .query(async ({ input }) => {
        const { getNoteBySlug } = await import("./db");
        const note = await getNoteBySlug(input.slug);
        
        if (!note) {
          throw new TRPCError({
            code: "NOT_FOUND",
            message: "Note not found",
          });
        }

        // Return note info but hide content if password-protected
        return {
          id: note.id,
          slug: note.slug,
          title: note.title,
          content: note.password ? null : note.content,
          hasPassword: !!note.password,
          userId: note.userId,
          createdAt: note.createdAt,
          updatedAt: note.updatedAt,
        };
      }),

    // Verify password and get full note content
    verifyPassword: publicProcedure
      .input(
        z.object({
          slug: z.string(),
          password: z.string(),
        })
      )
      .mutation(async ({ input }) => {
        const { getNoteBySlug, verifyNotePassword } = await import("./db");
        const note = await getNoteBySlug(input.slug);
        
        if (!note) {
          throw new TRPCError({
            code: "NOT_FOUND",
            message: "Note not found",
          });
        }

        const isValid = await verifyNotePassword(note, input.password);
        if (!isValid) {
          throw new TRPCError({
            code: "UNAUTHORIZED",
            message: "Incorrect password",
          });
        }

        return {
          id: note.id,
          slug: note.slug,
          title: note.title,
          content: note.content,
          createdAt: note.createdAt,
          updatedAt: note.updatedAt,
        };
      }),

    // List all notes for the current user
    myNotes: protectedProcedure.query(async ({ ctx }) => {
      const { getNotesByUserId } = await import("./db");
      return await getNotesByUserId(ctx.user.id);
    }),

    // Update a note (only by owner)
    update: protectedProcedure
      .input(
        z.object({
          id: z.string(),
          title: z.string().optional(),
          content: z.string().optional(),
          password: z.string().nullable().optional(),
        })
      )
      .mutation(async ({ ctx, input }) => {
        const { getNoteBySlug, updateNote } = await import("./db");
        const { getDb } = await import("./db");
        const { notes } = await import("../drizzle/schema");
        const { eq } = await import("drizzle-orm");
        
        const db = await getDb();
        if (!db) throw new TRPCError({ code: "INTERNAL_SERVER_ERROR" });
        
        // Verify ownership
        const [note] = await db.select().from(notes).where(eq(notes.id, input.id)).limit(1);
        if (!note || note.userId !== ctx.user.id) {
          throw new TRPCError({
            code: "FORBIDDEN",
            message: "You can only update your own notes",
          });
        }

        await updateNote(input.id, {
          title: input.title,
          content: input.content,
          password: input.password,
        });

        return { success: true };
      }),

    // Delete a note (only by owner)
    delete: protectedProcedure
      .input(z.object({ id: z.string() }))
      .mutation(async ({ ctx, input }) => {
        const { deleteNote, getDb } = await import("./db");
        const { notes } = await import("../drizzle/schema");
        const { eq } = await import("drizzle-orm");
        
        const db = await getDb();
        if (!db) throw new TRPCError({ code: "INTERNAL_SERVER_ERROR" });
        
        // Verify ownership
        const [note] = await db.select().from(notes).where(eq(notes.id, input.id)).limit(1);
        if (!note || note.userId !== ctx.user.id) {
          throw new TRPCError({
            code: "FORBIDDEN",
            message: "You can only delete your own notes",
          });
        }

        await deleteNote(input.id);
        return { success: true };
      }),
  }),
});

export type AppRouter = typeof appRouter;
