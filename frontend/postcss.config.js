export default {
  plugins: {
    'postcss-px-to-viewport': {
      viewportWidth: 375, // 设计稿宽度
      viewportHeight: 667, // 设计稿高度
      unitPrecision: 3, // 转换后的精度
      viewportUnit: 'vw', // 指定需要转换成的视窗单位
      selectorBlackList: ['.ignore', '.hairlines'], // 指定不转换为视窗单位的类
      minPixelValue: 1, // 小于或等于1px不转换为视窗单位
      mediaQuery: false, // 允许在媒体查询中转换px
    },
    autoprefixer: {},
  },
}

