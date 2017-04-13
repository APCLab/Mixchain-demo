<template lang="pug">
  div
    h2 MIXchain Recent Blocks
    table.ui.celled.table
      thead
        tr
          th Index
          th Block Hash
          th Tx Count
          th Timestamp
      tbody
        tr(
          v-for="block in blocks"
          v-bind:class="{'highlight': !!(block.tx.length >= 2)}"
        )
          td {{ block.height }}
          td
            router-link(
              v-bind:to="{name: 'detail', params: {blockId: block.height}}"
            ) {{ block.hash }}
          td {{ block.tx.length }}
          td {{ moment(block.time * 1000).fromNow() }}
</template>

<script>
import moment from 'moment'

export default {
  data() {
    return {
      blockcount: null,
      blocks: [],
      moment,
    }
  },
  mounted(){
    this.blockinfo()
  },
  methods: {
    blockinfo(){
      let url = 'blockinfo/'
      if (this.blockcount !== null)
        url = `blockinfo/?since=${this.blockcount}`

      this.$http.get(url).then(
        res => res.json(),
        res => {
          console.error(res.json())
          setTimeout(this.blockinfo, 800);
          return null
        }
      ).then(
        data => {
          if (data === null)
            return

          if (this.blockcount === null) {
            this.blockcount = data.blockcount
            this.blocks = data.blocks;
          }
          else {
            this.blockcount = data.blockcount
            data.blocks.reverse()
            data.blocks.map(function(val) {
              this.blocks.pop()
              this.blocks.unshift(val)
            }, this)
          }

          setTimeout(this.blockinfo, 800);
        }
      )
    },
  },
}
</script>

<style scoped>
tr.highlight {
  background-color: #fef7aa;
}
</style>
