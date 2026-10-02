const test = require('node:test');
const assert = require('node:assert/strict');
const Provider = require('./provider.cjs');
test('provider só aceita os dois recuperadores revisados', () => {
  assert.throws(() => new Provider({config: {mode: 'openai'}}));
});
test('preserva erro jurídico, paráfrase e abstenção', async () => {
  const literal = new Provider({config: {mode: 'literal'}});
  const expanded = new Provider({config: {mode: 'equivalencias'}});
  assert.equal((await literal.callApi('Quando começa?')).output, 'SEM_TRECHO');
  assert.equal((await expanded.callApi('Quando começa?')).output, 'prazo');
  assert.equal((await expanded.callApi('Quanto é a multa de rescisão?')).output, 'rescisao');
  assert.equal((await expanded.callApi('cor logotipo')).output, 'SEM_TRECHO');
});
