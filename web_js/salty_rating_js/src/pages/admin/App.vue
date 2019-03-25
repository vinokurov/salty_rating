<template>
  <div id="app">
    <b-container fluid>

      <b-container>

        <label for="input-title">Contest Title:</label>
        <b-form-input id="input-title" size="lg" type="text" v-model="contest_name" />

        <p class="mt-3 mb-1"><label>Contest UID: {{contest_uid}}</label></p>
        <p class="mb-1"><label>Active: {{contest_active}}</label></p>

        <b-form-checkbox class="mt-3"
          id="checkbox1"
          name="checkbox1"
          v-model="single_highlight"
          :value="true"
          :unchecked-value="false"
        >
          Single highlight mode
        </b-form-checkbox>

        <div class="mt-3">
          <b-modal
            ref="edit_contestants"
            @ok="applyContestantsAsText()"
            >
            <h3>Contestants</h3>
            <b-form-textarea
              v-model="contestants_as_text"
              rows="20"
            />
          </b-modal>
          <strong size="lg">Contestants</strong>&nbsp;
          <b-button size="sm" @click="editContestantsAsText()">Edit</b-button>
        </div>


        <b-list-group class="mt-3">
          <b-list-group-item
            v-for="contestant in contestants"
            :key="contestant"
            button
            @click="toggleContestant(contestant)"
            :active="highlighted.indexOf(contestant) >= 0">
            {{contestant}} <span class="close" v-on:click.stop="removeContestant(contestant)">x</span>
          </b-list-group-item>
        </b-list-group>

        <b-form-input  class="mt-3"
            type="text"
            v-model="new_contestant"
            @keydown.enter.prevent='addContestant'
            placeholder="Add contestant..."
        />


      </b-container>

      <b-container class="mt-3" v-if="contest_active">
        <div>
          <b-modal ref="modal_stop" @ok="stopContest">
            Are you sure you want to STOP the contest?
          </b-modal>

          <b-button block variant="danger" size="lg" @click="RequestStopContest">Stop Contest</b-button>
        </div>
      </b-container>
      <b-container class="mt-3" v-else>
        <div>
          <b-modal ref="modal_start" @ok="startContest">
            Are you sure you want to start the contest?
          </b-modal>

          <b-button block variant="success" size="lg" @click="RequestStartContest">Start Contest</b-button>
        </div>
      </b-container>

      <b-container class="mt-3" v-if="contest_uid">
        <div>
          <b-button block variant="primary" size="lg" @click="LoadContestResults">Get Results</b-button>
          <b-table
            striped
            hover
            :fields="results_fields"
            :items="results_table_items"
             />
        </div>
      </b-container>

    </b-container>
  </div>
</template>

<script>
import * as Ably from 'ably';
import axios from 'axios';
import EmojiRating from '../../components/EmojiRating.vue';
export default {
  name: 'app',
  components: {
    EmojiRating,
  },
  created() {
      this.client = new Ably.Realtime('iu0Lmw.hC3rhw:MEeGgoGc7kI4xQa1');
      this.channel_control = this.client.channels.get("rating_control");
      this.channel_highlights = this.client.channels.get("rating_highlights");
      this.loadLatestContestConfig()
  },
  data: function() {
    return {
        client: null,
        channel_control: null,
        channel_highlights: null,

        contest_name: '',
        contestants: ['22', '33', '12'],
        contest_uid: '',
        contest_active: true,

        highlighted: [],
        single_highlight: false,

        new_contestant: '',
        contestants_as_text: '',

        results: null,
        results_table_items: [],
        results_fields: [
          {key: 'Participant',sortable: true},
          {key: 'Total',sortable: true},
          {key: 'Judges',sortable: true},
          {key: 'Audience',sortable: true},
          {key: 'Count Total',sortable: true},
          {key: 'Count Judges',sortable: true},
          {key: 'Count Audience',sortable: true},
        ]

    }
  },
  methods: {
    addContestant: function() {
      if ((this.new_contestant != '') && (this.contestants.indexOf(this.new_contestant) == -1)) {
        this.contestants.push(this.new_contestant);
        this.new_contestant = '';
      }
    },
    removeContestant: function(contestant) {
      this.contestants.splice(this.highlighted.indexOf(contestant), 1)
      if(this.highlighted.indexOf(contestant) >= 0) {
        this.highlighted.splice(this.highlighted.indexOf(contestant), 1)
      }
    },
    toggleContestant: function(contestant) {
      if(this.highlighted.indexOf(contestant) >= 0) {
        this.highlighted.splice(this.highlighted.indexOf(contestant), 1)
      } else {
        if (this.contestants.indexOf(contestant) >= 0) {
          if(this.single_highlight)
            this.highlighted = [contestant]
          else
            this.highlighted.push(contestant)
        }
      }
    },
    startContest: async function() {
      // this.contest_active = true
      const url = '/rating/admin/new'
      let response = await axios.post(url, this.contest_config)
      this.setContestConfig(response.data);
      this.channel_control.publish("contest_config", this.contest_config);
    },
    RequestStartContest: function() {
      this.$refs.modal_start.show()
    },
    stopContest: async function() {
      this.contest_active = false
      this.channel_control.publish("contest_config", this.contest_config);
      const url = '/rating/admin/stop'
      let response = await axios.post(url, this.contest_config)
      // this.setContestConfig(response.data);
      console.log(response.data)
      this.results = response.data
    },
    RequestStopContest: function() {
      this.$refs.modal_stop.show()
    },
    editContestantsAsText: function() {
      this.contestants_as_text = this.contestants.join('\n');
      this.$refs.edit_contestants.show()
    },
    applyContestantsAsText: function() {
      this.contestants = this.contestants_as_text.match(/[^\r\n]+/g);
    },
    loadLatestContestConfig: async function() {
      const url = '/rating/contest_any'
      let response = await axios.get(url)
      console.log(response)
      this.setContestConfig(response.data);
    },
    setContestConfig: function(contest_config) {
      this.contest_name = contest_config.name || ''
      this.contest_uid = contest_config.contest_uid || ''
      this.contestants = contest_config.contestants || []
      this.contest_active = contest_config.active || false
      this.highlighted = []
    },
    LoadContestResults: async function() {
      const url = '/rating/admin/results'
      let response = await axios.post(url, this.contest_config)
      // this.setContestConfig(response.data);
      console.log(response)
      this.results = response.data
    },
  },
  watch: {
    ratings: {
      handler: function() {
        this.publishRatings()
      },
      deep: true
    },
    highlighted: function() {
      if(this.contest_active)
        this.channel_highlights.publish('highlighs', this.highlighted)
    },
    results: function() {
      this.results_table_items = []
      if(this.results) {
        console.log(this.results['Total'])
        Object.keys(this.results.Total).map(
          (key, index) => {
            let total = this.results.Total[key]
            let judges = this.results.Judges[key]
            let audience = this.results.Audience[key]

            this.results_table_items.push({
            Participant: key,
            Total: total == "N/A" ? total : total.toFixed(3),
            Audience: total == "N/A" ? total : audience.toFixed(3),
            Judges: judges == "N/A" ? judges : judges.toFixed(3),
            'Count Total': this.results['Count'][key],
            'Count Judges': this.results['Judges Cnt'][key],
            'Count Audience': this.results['Audience Cnt'][key],
          })}
        )
      }
    },
  },
  computed: {
    contest_config: function() {
      return {
        name: this.contest_name,
        contest_uid: this.contest_uid,
        contestants: this.contestants,
        active: this.contest_active,
      }

    },
  }
}
</script>

<style lang="scss">
@import '../../../style/custom-bootstrap.scss';
@import '../../../node_modules/bootstrap/scss/bootstrap.scss';
</style>
