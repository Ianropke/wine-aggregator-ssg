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
    retailer_name: z.string(),
    buy_url: z.string().url(),
    points: z.number(),
    qpr: z.number(),
    qpr_label: z.string().optional(),
    qpr_emoji: z.string().optional(),
    qpr_color: z.string().optional(),
    qpr_tagline: z.string().optional(),
    qpr_badge_img: z.string().optional(),
    estimated_price: z.number().optional(),
    vibe_category: z.string().optional(),
    food_pairing: z.array(z.string()).optional(),
    pros: z.array(z.string()).optional(),
    cons: z.array(z.string()).optional()
  }),
});

export const collections = {
  'wines': wineCollection,
};
