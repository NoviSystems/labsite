
Vue.config.keyCodes = {minus: 189};


const AutoScalingTest = Vue.extend({
    /**
     * Watch's a text value for changes and reports its width.
     */
    name: 'autoscaling-test',
    template: `<div ref="test" class="autoscaling-test" v-text="value"></div>`,
    props: ['name', 'value'],

    watch: {
        value() {
            // perform size check after the DOM updates.
            this.$nextTick(this.notify);
        },
    },

    methods: {
        notify() {
            const value = this.$refs.test.clientWidth;
            this.$emit('autoscale', this.name, value);
        },
    },
});


const AutoScalingInput = Vue.extend({
    /**
     * Reactively adjust an input's min-width and width attributes by it's placeholder and value properties.
     */
    name: 'autoscaling-input',
    template: `
        <span>
            <slot></slot>
            <autoscaling-test name="value" :value="value" @autoscale="updateWidth"></autoscaling-test>
            <autoscaling-test name="placeholder" :value="placeholder" @autoscale="updateWidth"></autoscaling-test>
        </span>`,
    components: {'autoscaling-test': AutoScalingTest},

    props: {
        'valueName': {default: 'value'},
        'placeholderName': {default: 'placeholder'},
    },

    data() {
        return {
            value: undefined,
            placeholder: undefined,
        };
    },

    mounted() {
        // there should only be one 'input' element.
        this.input = this.$el.getElementsByTagName('input')[0];

        // get the input's padding
        const style = window.getComputedStyle(this.input);
        const leftPad = Number(style['padding-left'].replace('px', ''));
        const rightPad = Number(style['padding-right'].replace('px', ''));

        this.padding = leftPad + rightPad;

        // setup value/placeholder watchers
        this.watchers = [
            this.$parent.$watch(this.valueName, this.updateValue, {immediate: true}),
        ];

        // placeholder may not be a reactive property
        if (this.placeholderName in this.$parent.$data)
            this.watchers.push(
                this.$parent.$watch(this.placeholderName, this.updatePlaceholder, {immediate: true})
            );
        else
            this.placeholder = this.input.placeholder;
    },

    beforeDestroy() {
        for (const unwatch in this.watchers)
            unwatch();
    },

    methods: {
        updateValue(value) {
            this.value = value
        },

        updatePlaceholder(value) {
            this.placeholder = value
        },

        updateWidth(name, value) {
            const attr = {
                value: 'width',
                placeholder: 'min-width',
            }[name];

            this.input.style[attr] = (value + this.padding) + 'px';
        },
    },
});


const BalanceInput = Vue.extend({
    name: 'balance-input',
    template: `
        <span class="no-wrap balance-input notify">
            <i class="fa fa-fw fa-exclamation dirty pull-left"
               v-show="isDirty"
               data-toggle="popover"
               data-placement="top"
               data-content="This field has changed.">
            </i>
            <autoscaling-input value-name="actual">
                <i class="fa fa-usd"></i>
                <input ref="input"
                       autocomplete="off"
                       :name="name"
                       v-model="actual"
                       :placeholder="placeholder"
                       @keydown.minus.prevent="negate"
                       @keydown="captureInput"
                       @focus="selectContents"
                       @input="update($event.target.value)">
            </autoscaling-input>
        </span>`,
    components: {'autoscaling-input': AutoScalingInput},
    props: ['name', 'value', 'initial', 'placeholder'],

    data() {
        let value = this.raw(this.value);
        value = this.isValid(value) ? this.format(value) : '';

        return {
            actual: value,
            validated: value,
        };
    },

    beforeCreate() {
        this.formatter = new Intl.NumberFormat('en-US', {
            style: 'decimal',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });
    },

    computed: {
        isDirty() {
            return this.raw(this.actual) !== this.raw(this.initial);
        },

        isNegative() {
            return this.validated.startsWith('-');
        },
    },

    methods: {
        isValid(value) {
            // empty and number strings validate
            return !isNaN(value) || value === '-';
        },

        raw(value) {
            if (isString(value)) {
                // strip only commas - NaN's desired for invalid chars
                value = value.replace(/,/g, '');

                // strip beyond two frac. digits - prevents rounding issues w/ format
                const dec = value.lastIndexOf('.');
                if (dec > 0)
                    value = value.substring(0, dec + 3)
            }

            return value;
        },

        format(value) {
            if (value === '' || value === '-')
                return value;

            // clear when removing leading digit
            if (value === '.00')
                return '';

            return this.formatter.format(value);
        },

        negate() {
            const makeNegative = !this.isNegative;

            const raw = this.validated === '' ? '' : Math.abs(this.raw(this.validated));
            const value = (makeNegative ? '-' : '') + raw;

            this.$nextTick(() => {
                this.update(value);
            });
        },

        captureInput(event) {
            this.position = event.target.selectionEnd;
            this.keyCode = event.keyCode;


            this.contentsSelected = (event.target.selectionStart === 0)
                && (event.target.selectionEnd === event.target.value.length);
        },

        computePosition(newValue) {
            // special case when going from empty to _.00
            if (this.validated === '')
                return 1;

            // special case for when contents are selected and replaced
            if (this.contentsSelected)
                return newValue.indexOf('.');

            let mod = newValue.length - this.validated.length;

            if (mod === 0) {
                // backspace handling
                if (this.keyCode === 8)
                    mod = -1;

                // type over commas, decimals
                else if ((this.keyCode === 188 && newValue.charAt(this.position) === ',')
                      || (this.keyCode === 190 && newValue.charAt(this.position) === '.'))
                    mod = 1;

                // if typing beyond decimal, length won't change so manually index
                else if (this.position > newValue.indexOf('.')) {
                    mod = 1;
                }
            }

            return Math.max(this.position + mod, 0);
        },

        update(value) {
            const raw = this.raw(value);
            const isValid = this.isValid(raw);

            // prevent removing decimal w/ backspace. otherwise values like 1.00 would reformat as 100.00
            const decimalCheck = (this.validated.charAt(this.position-1) !== '.') || (this.keyCode !== 8);

            // prevent more than 8 digits. no need to check fractional part, as it's always 2
            const lengthCheck = (raw.split('.')[0].length <= 8);

            const newValue = isValid && decimalCheck && lengthCheck
                ? this.format(raw)
                : this.validated;

            const newPosition = this.computePosition(newValue);

            // set input value
            this.validated = newValue;
            this.actual = newValue;

            // restore cursor positions
            this.$nextTick(() => {
                this.$refs.input.selectionStart = newPosition;
                this.$refs.input.selectionEnd = newPosition;
            });
        },

        selectContents(event) {
            event.target.select();
        },
    },
});
