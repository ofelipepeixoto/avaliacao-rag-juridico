// Adaptação original: chama o recuperador Python existente, sem provider de rede.
const {execFileSync} = require('node:child_process');
const path = require('node:path');
module.exports = class LocalRetriever {
  constructor(options) {
    this.mode = options.config?.mode;
    if (!['literal', 'equivalencias'].includes(this.mode)) throw new Error('Modo não permitido');
  }
  id() { return `local-${this.mode}`; }
  async callApi(prompt) {
    const output = execFileSync('python3', [path.join(__dirname, 'retrieve.py'), this.mode], {
      input: JSON.stringify({question: prompt}), encoding: 'utf8', timeout: 5000,
      maxBuffer: 16384, env: {PATH: process.env.PATH, PYTHONDONTWRITEBYTECODE: '1'},
    });
    return {output: JSON.parse(output).output};
  }
};
