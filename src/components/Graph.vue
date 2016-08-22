<template>
  <div class="graph">
    <button class="stop" @click="stopAnimation">stop</button>
    <button class="start" @click="startAnimation">start</button>
    <svg version="1.1" width="1000" height="500" xmlns="http://www.w3.org/2000/svg">
    </svg>
  </div>
</template>

<script>
/* eslint-disable no-unused-vars, no-undef, no-unreachable, no-debugger */
import 'whatwg-fetch'
import _ from 'lodash'
import Snap from 'imports-loader?this=>window,fix=>module.exports=0!snapsvg/dist/snap.svg.js'

var timingRequest = fetch('/static/timing.json').then(resp => resp.json())
var networkInRequest = fetch('/static/network-in.json').then(resp => resp.json())

let snap = null

let absoluteStart = null
let entityCount = null

let networkIn = null
let networkInIndex = 1
let networkInAnimationStart = null
let networkInXUnit = null
let networkInYUnit = null

let timing = null
let timingXUnit = 0
let timingYUnit = null
let timingIndices = {}
let timingPositions = {}
let timingRects = {}
let timingAnimationStart = null

var drawTiming = (inst, animationOffset) => {
  // depends on `timing*` outer scope vars above
  animationOffset = animationOffset * 5000 // go faster
  if (!timingAnimationStart) {
    timingAnimationStart = animationOffset
  }
  let animationTimestamp = absoluteStart + (animationOffset - timingAnimationStart)
  _.map(timing, (dataPoints, entityName) => {
    var index = timingIndices[entityName]
    if (dataPoints.length <= index) {
      return
    } else {
      var [requestTimestamp, requestDuration] = dataPoints[index]
    }
    requestTimestamp = requestTimestamp * 1000
    if (animationTimestamp >= requestTimestamp) {
      let x = timingPositions[entityName] * timingXUnit + 100
      let y = 500 - ((index + 1) * timingYUnit)
      let graphPoint = snap.rect(x, y, timingXUnit, timingYUnit)
      graphPoint.attr({fill: 'grey'})
      // graphPoint.animate({fill: 'grey'}, requestDuration * 10)
      timingIndices[entityName] += 1
    }
  })
  if (inst.animationState !== 0) {
    window.requestAnimationFrame(_.partial(drawTiming, inst))
  }
}

var drawNetworkIn = (inst, animationOffset) => {
  // depends on `timing` and `networkIn` above
  animationOffset = animationOffset * 5000 // go faster
  if (!networkInAnimationStart) { networkInAnimationStart = animationOffset }
  let animationTimestamp = absoluteStart + (animationOffset - networkInAnimationStart)
  if (networkIn.length <= networkInIndex) {
    return
  } else {
    var datapoint = networkIn[networkInIndex]
  }
  let prevDatapoint = networkIn[networkInIndex - 1]
  let networkInTimestamp = new Date(datapoint.timestamp).getTime()
  if (animationTimestamp >= networkInTimestamp) {
    let x1 = networkInXUnit * networkInIndex - 1
    let y1 = 500 - (networkInYUnit * prevDatapoint.bytesIn)
    let x2 = networkInXUnit * networkInIndex
    let y2 = 500 - (networkInYUnit * datapoint.bytesIn)
    let line = snap.line(x1, y1, x2, y2)
    line.attr({stroke: 'blue'})
    networkInIndex += 1
  }
  if (inst.animationState !== 0) {
    window.requestAnimationFrame(_.partial(drawNetworkIn, inst))
  }
}

var degranularise = (timing, denominator) => {
  // average by denominator
  let out = {}
  _.map(timing, (timings, entityName) => {
    out[entityName] = _.reduce(
      timings,
      (acc, [time, duration], index) => {
        if (index % denominator !== 0 || index === 0) { return acc }
        let [sumTime, sumDuration] = _.reduce(
          _.slice(timings, index - denominator, index),
          ([aggTime, aggDuration], [time_, duration_]) => {
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
      animationState: 0,
      drawTimingAnimId: null
    }
  },
  methods: {
    stopAnimation: function () {
      this.animationState = 0
      window.cancelAnimationFrame(this.drawTimingAnimId)
      window.cancelAnimationFrame(this.drawNetowrkInAnimId)
    },
    startAnimation: function () {
      this.drawTimingAnimId = window.requestAnimationFrame(_.partial(drawTiming, this))
      this.drawNetworkInAnimId = window.requestAnimationFrame(_.partial(drawNetworkIn, this))
    }
  },
  ready: function () {
    snap = Snap('svg')
    var inst = this

    Promise.all([timingRequest, networkInRequest]).then(([timingInner, networkInDataInner]) => {
      var entityNames = Object.keys(timingInner)
      entityCount = entityNames.length
      timingXUnit = (1000 / entityCount)
      timingInner = degranularise(timingInner, 4)
      let maxReqCount = 0
      _.map(entityNames, (entityName, index) => {
        timingIndices[entityName] = 0
        timingPositions[entityName] = index + 1
        if (timingInner[entityName].length > maxReqCount) {
          maxReqCount = timingInner[entityName].length
        }
      })
      timingYUnit = (500 / maxReqCount) * 5

      networkInXUnit = 100 / networkInDataInner.length
      let maxBytes = 0
      _.map(networkInDataInner, ({Average}) => {
        if (Average > maxBytes) {
          maxBytes = Average
        }
      })
      networkInYUnit = 500 / maxBytes
      networkInXUnit = 1000 / networkInDataInner.length

      timing = timingInner
      networkIn = _.sortBy(_.map(networkInDataInner, ({Timestamp, Average}) => {
        return {
          timestamp: new Date(Timestamp).getTime(),
          bytesIn: Average
        }
      }), 'timestamp')

      absoluteStart = networkIn[0].timestamp

      inst.animationState = 1
      inst.startAnimation()
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
svg {
  border: 1px solid black;
}
</style>
