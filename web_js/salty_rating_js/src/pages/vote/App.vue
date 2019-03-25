<template>
  <div id="app">

    <b-jumbotron
      header="Salty Rating"
      header-level=4
      lead="Mind the Shag ☆ London Shag Festival"
      bg-variant="danger"
      fluid
      />

    <b-container fluid v-if="contest_active">

      <b-container class="mt-5">
        <h2>Contest: {{contest_name}}</h2>
      </b-container>

      <b-container class="mt-3">
        <b-form-input class="mt-3"
          type="text"
          v-model="voter_name"
          placeholder="Please enter your name..."
        />
      </b-container>


      <b-container class="mt-5">
        <b-list-group>
          <b-list-group-item
            v-for="contestant in contestants"
            :id="'contestant-item-'+contestant"
            :key="contestant"
            :active="highlighted.indexOf(contestant) >= 0"
            >
            <strong>{{contestant}}</strong>
            <star-rating
              v-if="use_stars"
              v-model="ratings[contestant]"
              :show-rating="false"
              :star-size="40"
            />
            <emoji-rating
              v-resize-text
              v-if="!use_stars"
              v-model="ratings[contestant]"
              variant_active="dark-orange"
              size="lg"
              style="white-space: nowrap;"
            />
          </b-list-group-item>
        </b-list-group>

    </b-container>

  </b-container>

  <b-container fluid v-else>
    <b-container class="mt-5">
      <h2>
        The contest is either finished or not started yet..
      </h2>
    </b-container>
  </b-container>

  <b-navbar toggleable="lg" type="dark" variant="danger" class="sticky-bottom mt-5">
    <b-container fluid>
      By Alex Vinokurov / Salty Jitterbugs
    </b-container>
  </b-navbar>
</div>
</template>

<script>
import * as Ably from 'ably';
import axios from 'axios';
import StarRating from 'vue-star-rating';
import ResizeText from 'vue-resize-text';
import EmojiRating from '../../components/EmojiRating.vue';
// import FontAwesome from '../../components/FontAwesome.vue';
// import posed, { PoseTransition } from "vue-pose";
export default {
  name: 'app',
  components: {
    EmojiRating,
    // FontAwesome,
    StarRating,
    // Box: posed.div({
    //   pressable: true,
    //   init: { scale: 1 },
    //   press: { scale: ({active}) => active?1.2:1 },
    // }),
  },
  directives: {
    ResizeText,
  },
  created() {
      this.client = new Ably.Realtime('iu0Lmw.hC3rhw:MEeGgoGc7kI4xQa1');
      this.channel_control = this.client.channels.get("rating_control");
      this.channel_control.subscribe('contest_config', this.updateContest);

      this.channel_highlights = this.client.channels.get("rating_highlights");
      this.channel_highlights.subscribe('highlighs', this.updateHighlights);

      this.loadLatestContestConfig()
  },
  data: function() {
    return {
        client: null,
        channel_control: null,
        channel_highlights: null,

        voter_name: '',

        contest_name: 'Undefined',
        contestants: ['22', '33', '12'],
        contest_uid: '',
        contest_active: false,

        highlighted: [],

        ratings: {},
        use_stars: false,
    }
  },
  methods: {
    publishRatings: async function() {
      if(this.contest_active) {
         console.log('publishRatings', this.ratings)
         const url = '/rating/vote/submit'
         await axios.post(url, this.ratings_data)
      }
    },
    updateContest(message) {
      console.log(message)
      this.ratings = {};
      this.setContestConfig(message.data)
    },
    updateHighlights(message) {
      console.log.message;
      this.highlighted = message.data;
      let item = 'contestant-item-' + this.highlighted[0];
      if(this.highlighted.length > 0)
      setTimeout(function() {
          document.getElementById(item).scrollIntoView();
      }, 100);
    },
    loadLatestContestConfig: async function() {
      const url = '/rating/contest'
      let response = await axios.get(url)
      console.log(response)
      this.setContestConfig(response.data);
      this.loadLatestRating()
    },
    setContestConfig: function(contest_config) {
      this.contest_name = contest_config.name || ''
      this.contest_uid = contest_config.contest_uid || ''
      this.contestants = contest_config.contestants || []
      this.contest_active = contest_config.active || false
      this.highlighted = []
    },
    loadLatestRating: async function() {
      const url = '/rating/my_vote'
      let response = await axios.post(url, {contest_uid: this.contest_uid})
      console.log(response)
      this.ratings = response.data.ratings || {}
      this.voter_name = response.data.name
    },

  },
  watch: {
    ratings: {
      handler: function() {
        this.publishRatings()
      },
      deep: true
    },
  },
  computed: {
    ratings_data: function(){
      return {
        name: this.voter_name,
        contest_uid: this.contest_uid,
        ratings: this.ratings
      }
    },
  }
}
</script>

<style lang="scss">
@import '../../../style/custom-bootstrap.scss';
@import '../../../node_modules/bootstrap/scss/bootstrap.scss';
</style>
