import {
  defineConfig,
  presetAttributify,
  presetUno,
  transformerVariantGroup,
  transformerDirectives,
} from 'unocss'

export default defineConfig({
  shortcuts: [
    ['btn', 'px-4 py-2 rounded font-semibold transition-all cursor-pointer active:scale-95 disabled:cursor-not-allowed disabled:opacity-50 border-none'],
    ['btn-primary', 'btn bg-sky-500 hover:bg-sky-600 text-white shadow-lg shadow-sky-500/30'],
    ['btn-success', 'btn bg-emerald-500 hover:bg-emerald-600 text-white shadow-lg shadow-emerald-500/30'],
    ['btn-ghost', 'btn bg-white/10 hover:bg-white/20 text-white'],
    ['card', 'bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-6 shadow-xl'],
    ['input-text', 'bg-white/10 border border-white/20 rounded px-4 py-2 text-white outline-none focus:border-sky-500/50 focus:bg-white/15 transition-all w-full'],
  ],
  presets: [
    presetUno(),
    presetAttributify(),
  ],
  transformers: [
    transformerVariantGroup(),
    transformerDirectives(),
  ],
})
