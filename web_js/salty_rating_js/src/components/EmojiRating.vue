<template>
	<div>
		<i
			v-for="icon in icons" :key="icon.score"
			:class="icon_classes(icon.icon, icon.score)"
			aria-hidden="true"
			@click="set_score(icon.score)"
		/>
	</div>
</template>

<script>
export default {
  name: 'EmojiRating',
	props: {
    variant_active: { type: String, default: "primary"},
    variant_inactive: { type: String, default: "muted"},
		size: { type: String, default: "2x"},
    value: { type: Number, default: 0 },
  },
	data: function() {return {
		icons: [
			{score:1, title:'Very Bad', icon:'tired'},
			{score:2, title:'Bad', icon:'frown'},
			{score:3, title:'Normal', icon:'meh-rolling-eyes'},
			{score:4, title:'Good', icon:'smile'},
			{score:5, title:'Super Cool', icon:'grin-stars'},
		],
		rating_score: 0,
	}},
	methods: {
		set_score: function(icon_score) {
			this.rating_score = icon_score;
			this.$emit('input', this.rating_score);
			this.$emit('change', this.rating_score);
		},
		text_color_class: function(icon_score) {
			if (icon_score === this.value)
				return 'text-' + this.variant_active
			else
				return 'text-' + this.variant_inactive
		},
		icon_classes: function(icon_name, icon_score){
			let classes = [
				'fa-fw',
				'fa-' + icon_name,
				'fa-'+this.size,
			]
			if (icon_score === this.value){
				classes.push('fas')
				classes.push('text-' + this.variant_active)
			}else {
				classes.push('far')
				classes.push('text-' + this.variant_inactive)
			}

			return classes.join(' ')
		},
	},
	watch: {
		value: function() {
			this.rating_score = this.value;
		}
	},
}
</script>
