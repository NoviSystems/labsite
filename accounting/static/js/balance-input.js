
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
                       :maxlength="maxlength"
                       :name="name"
                       v-model="actual"
                       :placeholder="placeholder"
                       @keydown.minus.prevent="negate"
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
            maximumFractionDigits: 0,
        });
    },

    computed: {
        isDirty() {
            return this.raw(this.actual) !== this.raw(this.initial);
        },

        isNegative() {
            return this.validated.startsWith('-');
        },

        maxlength() {
            // maxlength of 10 is 8 digits + 2 comma separators
            return this.isNegative ? 11 : 10;
        },
    },

    methods: {
        isValid(value) {
            // empty and number strings validate
            return !isNaN(value) || value === '-';
        },

        raw(value) {
            // strip only commas - NaN's desired for invalid chars
            if (isString(value))
                value = value.replace(/,/g, '');
            return value;
        },

        format(value) {
            if (value === '' || value === '-')
                return value;
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

        update(value) {
            const raw = this.raw(value);
            const isValid = this.isValid(raw);
            const newValue = isValid ? this.format(raw) : this.validated;

            // capture cursor postion
            const position = this.$refs.input.selectionEnd;

            // TODO: the new position calculations are kind of a mess - need to rework this.
            let mod;
            if (isValid) {
                const negated = (this.raw(newValue) * -1) == (this.raw(this.validated) * 1);
                const diff = Math.abs(newValue.length - this.validated.length) > 1
                    ? 1
                    : negated ? 1 : 0;
                const direction = newValue.length >= this.validated.length ? 1 : -1;

                mod = diff * direction;
            } else {
                // invalid value implies letter entry - move caret back.
                mod = -1;
            }

            // set input value
            this.validated = newValue;
            this.actual = newValue;

            // restore cursor positions
            this.$nextTick(() => {
                // hack to handle field clearing
                let newPosition = value.length === 1 ? 1 : (position + mod);
                if (newPosition < 0)
                    newPosition = 0;

                this.$refs.input.selectionStart = newPosition;
                this.$refs.input.selectionEnd = newPosition;
            });
        },

        selectContents(event) {
            event.target.select();
        },
    },
});
