# Cucumber.js (TypeScript) Implementation

## Setup

```bash
npm install --save-dev @cucumber/cucumber ts-node typescript
```

Layout:
```
features/
  checkout.feature
features/step_definitions/
  checkout.steps.ts
features/support/
  world.ts
```

## Config (`cucumber.js` in project root)

```javascript
module.exports = {
  default: {
    requireModule: ['ts-node/register'],
    require: ['features/**/*.ts'],
    paths: ['features/**/*.feature'],
  },
};
```

## Step Definitions

```typescript
import { Given, When, Then } from '@cucumber/cucumber';
import assert from 'node:assert';
import { CartWorld } from './../support/world';

Given('the cart contains a {string}', function (this: CartWorld, item: string) {
  this.cart.add(item);
});

When('the user checks out', function (this: CartWorld) {
  this.cart.checkout();
});

Then('the order total is {int}', function (this: CartWorld, total: number) {
  assert.strictEqual(this.cart.total, total);
});
```

## World (per-scenario state)

```typescript
import { setWorldConstructor } from '@cucumber/cucumber';
import { Cart } from '../../src/cart';

export class CartWorld {
  cart = new Cart();
}
setWorldConstructor(CartWorld);
```

## Hooks

```typescript
import { Before, After } from '@cucumber/cucumber';

Before(function () { /* arrange */ });
After(function () { /* cleanup */ });
```

## Run

```bash
npx cucumber-js
# Filter by tag:
npx cucumber-js --tags "@smoke"
```
Expected: each scenario reported as passing.
