import {
  defineConfig,
  presetAttributify,
  presetUno,
  transformerVariantGroup,
  transformerDirectives,
} from 'unocss'

export default defineConfig({
  shortcuts: [
    ['btn', 'px-4 py-2 rounded font-semibold transition-all cursor-pointer active:scale-95 disabled:cursor-not-allowed disabled:opacity-50 border-none inline-flex items-center justify-center'],
    ['btn-primary', 'btn bg-sky-500 hover:bg-sky-600 text-white shadow-lg shadow-sky-500/30'],
    ['btn-success', 'btn bg-emerald-500 hover:bg-emerald-600 text-white shadow-lg shadow-emerald-500/30'],
    ['btn-ghost', 'btn bg-white/10 hover:bg-white/20 text-white'],
    ['card', 'bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-6 shadow-xl'],
    ['input-text', 'bg-white/10 border border-white/20 rounded px-4 py-2 text-white outline-none focus:border-sky-500/50 focus:bg-white/15 transition-all w-full'],
    ['radar-scan', 'w-100px h-100px border-rd-50% border-2 border-sky-400/30 relative overflow-hidden bg-[radial-gradient(circle,rgba(56,189,248,0.1)_0%,transparent_70%)] after:content-[""] after:absolute after:top-50% after:left-50% after:w-100% after:h-100% after:bg-[conic-gradient(from_0deg,#38bdf8_0deg,transparent_90deg)] after:origin-top-left after:animate-radar'],
  ],
  presets: [
    presetUno(),
    presetAttributify(),
  ],
  transformers: [
    transformerVariantGroup(),
    transformerDirectives(),
  ],
  rules: [
    [/^grid-board$/, () => ({
      display: 'inline-grid',
      'grid-template-columns': '1.5rem repeat(10, min(3.8vh, 7.2vw))',
      'grid-template-rows': '1.5rem repeat(10, min(3.8vh, 7.2vw))',
    })],
  ],
  theme: {
    animation: {
      keyframes: {
        radar: '{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}',
      },
      durations: {
        radar: '2s',
      },
      timingFns: {
        radar: 'linear',
      },
      counts: {
        radar: 'infinite',
      },
    },
  },
})
