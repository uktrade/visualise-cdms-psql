<template>
  <div class="graph">
    <button class="stop" @click="stopTimingAnim">stop</button>
    <button class="start" @click="startTimingAnim">start</button>
    <svg version="1.1" width="700" height="700" xmlns="http://www.w3.org/2000/svg">
    </svg>
  </div>
</template>

<script>
/* eslint-disable no-unused-vars, no-undef */
import 'whatwg-fetch'
import _ from 'lodash'
import Snap from 'imports-loader?this=>window,fix=>module.exports=0!snapsvg/dist/snap.svg.js'

var timingRequest = fetch('/static/timing.json').then(resp => resp.json())
var networkInRequest = fetch('/static/network-in.json').then(resp => resp.json())

let snap = null

let absoluteStart = null
let entityCount = null

let networkIn = null
let networkInAnimationStart = null

let timing = null
let timingXUnit = 0
let timingYUnit = null
let timingIndices = {}
let timingPositions = {}
let timingAnimationStart = null

var drawTiming = (inst, animationOffset) => {
  // depends on `timing*` outer scope vars above
  if (!timingAnimationStart) {
    timingAnimationStart = animationOffset
  }
  var animationTimestamp = absoluteStart + (timingAnimationStart - animationOffset)
  _.map(timing, (dataPoints, entityName) => {
    var index = timingIndices[entityName]
    if (dataPoints.length <= index) {
      return
    } else {
      var [requestTimestamp, requestDuration] = dataPoints[index]
    }
    if (animationTimestamp >= requestTimestamp) {
      // debugger
      let x = timingPositions[entityName] * timingXUnit + 100
      let y = 700 - ((index + 1) * timingYUnit)
      let graphPoint = snap.rect(x, y, timingXUnit, timingYUnit)
      graphPoint.attr({fill: 'black'})
      timingIndices[entityName] += 1
    } else {
      console.log('ever?')
    }
  })
  if (inst.timingState !== 0) {
    window.requestAnimationFrame(_.partial(drawTiming, inst))
  }
}

var drawNetworkIn = (timestamp) => {
  // depends on `timing` and `networkIn` above
  debugger
}

var degranularise = (timing, denominator) => {
  // average by denominator
  let out = {}
  _.map(timing, (timings, entityName) => {
    out[entityName] = _.reduce(
      timings,
      (acc, [time, duration], index) => {
        if (index % denominator === 0 || index === 0) { return acc }
        let [sumTime, sumDuration] = _.reduce(
          _.slice(timings, index, index - denominator),
          ([aggTime, aggDuration], time_, duration_) => {
            return [aggTime + time_, aggDuration + duration]
          },
          [0, 0]
        )
        acc.push([sumTime / denominator, sumDuration / denominator])
        return acc
      },
      []
    )
  })
  return out
}

export default {
  data: () => {
    return {
      /*
       * 0: stopped
       * 1: started
       */
      timingState: 0,
      drawTimingAnimId: null
    }
  },
  methods: {
    stopTimingAnim: function () {
      this.timingState = 0
      window.cancelAnimationFrame(this.drawTimingAnimId)
    },
    startTimingAnim: function () {
      this.drawTimingAnimId = window.requestAnimationFrame(_.partial(drawTiming, this))
    },
    drawTiming: drawTiming
  },
  ready: function () {
    snap = Snap('svg')
    var inst = this

    Promise.all([timingRequest, networkInRequest]).then(([timingInner, networkInDataInner]) => {
      var entityNames = Object.keys(timingInner)
      entityCount = entityNames.length
      timingXUnit = 700 / entityCount
      console.log(_.sum(_.map(timingInner, 'length')))
      timingInner = degranularise(timingInner, 4)
      console.log(_.sum(_.map(timingInner, 'length')))
      let maxReqCount = 0
      _.map(entityNames, (entityName, index) => {
        timingIndices[entityName] = 0
        timingPositions[entityName] = index + 1
        if (timingInner[entityName].length > maxReqCount) {
          maxReqCount = timingInner[entityName].length
        }
      })
      timingYUnit = 700 / maxReqCount * 1
      timing = timingInner
      networkIn = networkInDataInner.Datapoints
      absoluteStart = new Date(networkInDataInner.Datapoints[0].Timestamp).getTime()
      inst.timingState = 1
      inst.drawTimingAnimId = window.requestAnimationFrame(_.partial(drawTiming, inst))
      /*
      setTimeout(() => {
        window.cancelAnimationFrame(drawTimingAnimId)
      }, 1000)
      */
      // window.requestAnimationFrame(drawNetworkIn)
    })
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h1 {
  color: #42b983;
}
button {
  position: fixed;
  left: 10px;
}
button.start {
  top: 10px;
}
button.stop {
  top: 30px;
}
</style>
