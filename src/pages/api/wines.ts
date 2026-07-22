import { getCollection } from 'astro:content';

export async function GET({ request }) {
  const wines = await getCollection('wines');
  
  // Format the response payload using exact schema field names
  const payload = wines.map(wine => ({
    id: wine.data.id,
    title: wine.data.title,
    vibe_category: wine.data.vibe_category,
    region: wine.data.region,
    vintage: wine.data.vintage,
    price: wine.data.price,
    bundle_size: wine.data.bundle_size || 1,
    points: wine.data.points,
    qpr: wine.data.qpr,
    retailer_name: wine.data.retailer_name,
    buy_url: wine.data.buy_url
  }));

  return new Response(JSON.stringify(payload), {
    status: 200,
    headers: {
      'Content-Type': 'application/json'
    }
  });
}

