import { z, defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';

const wineCollection = defineCollection({
  loader: glob({ pattern: "*.mdx", base: "./src/content/wines" }),
  schema: z.object({
    id: z.string(),
    title: z.string(),
    region: z.string(),
    vintage: z.number(),
    price: z.number(),
    bundle_size: z.number().optional(),
    points: z.number(),
    qpr: z.number(),
    estimated_price: z.number(),
    spotify_seed: z.string(),
    pros: z.array(z.string()),
    cons: z.array(z.string())
  }),
});

export const collections = {
  'wines': wineCollection,
};
