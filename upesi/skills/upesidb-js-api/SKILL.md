---
name: upesidb-js-api
description: UpesiDB JavaScript API reference. Use when writing browser-side code that reads or writes data with UpesiDB.
---

# UpesiDB JavaScript API

Complete reference for the UpesiDB browser client. This library provides a schemaless document database for static websites hosted on Upesi.

## Setup

```html
<script src="/_db/db.js"></script>
```

No further configuration needed. The script exposes `window.db` with the correct API key embedded.

**Prerequisite:** Call `upesi_db_key(app: "my-app")` once to create the API key.

## Accessing Collections

Collections are accessed as properties on `db`:

```javascript
db.posts      // → UpesiCollection for "posts"
db.users      // → UpesiCollection for "users"
db.order_items // → UpesiCollection for "order_items"
```

Collections are created automatically on first write. No setup needed.

**Collection naming rules:** lowercase letters, numbers, underscores. Must start with a letter. Max 63 chars.
- Valid: `posts`, `user_scores`, `items2`
- Invalid: `2fast`, `my-posts`, `Posts`

## Document Structure

Documents are flat — your fields are at the top level:

```javascript
{
  id: 42,
  title: "Hello",           // ← your field
  body: "World",            // ← your field
  created_at: "2025-01-15T...",
  updated_at: "2025-01-15T..."
}
```

`id`, `created_at`, and `updated_at` are managed by the server.

## CRUD Methods

All methods are async and return Promises.

### insert(data) → document

Create a new document. Returns the created document with `id`.

```javascript
const post = await db.posts.insert({ title: "Hello", body: "World" });
console.log(post.id);    // 42
console.log(post.title); // "Hello"
```

### find(filter?, options?) → { data, total, limit, offset }

Query documents. Returns paginated result.

```javascript
// All documents
const result = await db.posts.find();
result.data.forEach(doc => console.log(doc.title));

// With filter
const result = await db.posts.find({ status: "published" });

// With filter, sorting, and pagination
const result = await db.posts.find(
  { status: "published" },
  { sort: { created_at: -1 }, limit: 10, offset: 0 }
);
```

### findOne(id) → document

Get a single document by ID.

```javascript
const post = await db.posts.findOne(42);
console.log(post.title); // "Hello"
```

### update(id, data) → document

Merge fields into an existing document. Unmentioned fields are preserved.

```javascript
await db.posts.update(42, { title: "New Title" });
// body is preserved, only title is updated
```

### replace(id, data) → document

Replace all user fields. Unmentioned fields are removed.

```javascript
await db.posts.replace(42, { title: "New" });
// body is gone, only title remains
```

### delete(id) → { deleted, id }

Delete a document.

```javascript
await db.posts.delete(42);
```

### count(filter?) → { count }

Count documents, optionally with a filter.

```javascript
const { count } = await db.posts.count();
const { count } = await db.posts.count({ status: "draft" });
```

## Filter Operators

Used in `find()` and `count()`:

| Operator | Example | Meaning |
|----------|---------|---------|
| *(exact)* | `{ age: 25 }` | Exact match |
| `$gt` | `{ age: { $gt: 18 } }` | Greater than |
| `$gte` | `{ age: { $gte: 18 } }` | Greater than or equal |
| `$lt` | `{ age: { $lt: 65 } }` | Less than |
| `$lte` | `{ age: { $lte: 65 } }` | Less than or equal |
| `$ne` | `{ status: { $ne: "draft" } }` | Not equal |
| `$in` | `{ tag: { $in: ["a", "b"] } }` | Value in array |
| `$or` | `{ $or: [{ a: 1 }, { b: 2 }] }` | Logical OR |

## Sorting

Pass `sort` in options to `find()`:

```javascript
{ sort: { created_at: -1 } }  // descending (newest first)
{ sort: { created_at: 1 } }   // ascending (oldest first)
```

## Pagination

Pass `limit` and `offset` in options to `find()`:

```javascript
{ limit: 10, offset: 20 }
```

- Default limit: 50
- Maximum limit: 1000

## Error Handling

Errors throw `UpesiError` with `code`, `message`, and `status`:

```javascript
try {
  await db.posts.insert({ title: "Hello" });
} catch (e) {
  console.error(e.code, e.message);
  // e.code: 'not_found' | 'unauthorized' | 'limit_exceeded' |
  //         'payload_too_large' | 'server_error' | 'rate_limit'
}
```

## Limits

| Resource | Limit |
|----------|-------|
| Document size | 1 MB |
| Documents per collection | 100,000 |
| Collections per app | 100 |

## Complete Example

```html
<script src="/_db/db.js"></script>
<script>
  async function main() {
    // Create
    const post = await db.posts.insert({ title: "Hello", status: "published" });

    // List published posts, newest first
    const { data: posts, total } = await db.posts.find(
      { status: "published" },
      { sort: { created_at: -1 }, limit: 10 }
    );
    posts.forEach(p => console.log(p.title));

    // Update
    await db.posts.update(post.id, { title: "Updated Title" });

    // Delete
    await db.posts.delete(post.id);
  }
  main();
</script>
```
