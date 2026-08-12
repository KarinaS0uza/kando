import { Slider as BaseSlider } from "@base-ui/react/slider";
import styles from "./Slider.module.css";

// Percentage slider (0-100) used on the Reliability page's two
// self-assessment questions. Wraps @base-ui/react/slider. Props:
// - value (number): current percentage
// - onChange (fn): called with the new value on drag
// Styled with CSS Modules (Slider.module.css) instead of a plain global
// stylesheet like the rest of the app - the only such case here, chosen
// because the classNames below (Track, Thumb, Indicator) mirror
// @base-ui/react's own subcomponent names, and module-scoping avoids that
// naming coinciding with anything else in the global stylesheet.
export default function Slider({ value, onChange }) {
  return (
    <div className={styles.slider}>
      <label className={styles.value}>{`0`}</label>
      <BaseSlider.Root
        className={styles.sliderRoot}
        value={value}
        onValueChange={onChange}
        min={0}
        max={100}
      >
        <BaseSlider.Control className={styles.Control}>
          <BaseSlider.Track className={styles.Track}>
            <BaseSlider.Indicator className={styles.Indicator} />
            <BaseSlider.Thumb aria-label="Volume" className={styles.Thumb} />
          </BaseSlider.Track>
        </BaseSlider.Control>
      </BaseSlider.Root>
      <label className={styles.value}>{`${value}%`}</label>
    </div>
  );
}
