import { getCollection } from 'astro:content';

export async function GET({ request }) {
  const wines = await getCollection('wines');
  
  // Format the response payload
  const payload = wines.map(wine => ({
    id: wine.id,
    name: wine.data.name,
    category: wine.data.category,
    price: wine.data.price,
    score: wine.data.score,
    qpr: wine.data.qpr,
    retailer: wine.data.retailer
  }));

  return new Response(JSON.stringify(payload), {
    status: 200,
    headers: {
      'Content-Type': 'application/json'
    }
  });
}
