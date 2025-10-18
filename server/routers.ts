import { systemRouter } from "./_core/systemRouter";
import { publicProcedure, protectedProcedure, router } from "./_core/trpc";
import { TRPCError } from "@trpc/server";
import { z } from "zod";

export const appRouter = router({
  system: systemRouter,
  notes: router({
    // Create a new note (public - no login required)
    create: publicProcedure
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
          userId: ctx.user?.id || null, // Allow anonymous notes
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
  }),
});

export type AppRouter = typeof appRouter;
