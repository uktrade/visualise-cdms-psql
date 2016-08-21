import Vue from 'vue'
import VueRouter from 'vue-router'

Vue.use(VueRouter)

import App from './App'
import Graph from './components/Graph'

const router = new VueRouter()

router.map({
  '/': {
    component: Graph
  }
})

router.start(Vue.extend(App), 'app')
