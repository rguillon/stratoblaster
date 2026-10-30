import { afterEach, describe, expect, it } from 'vitest';
import { NullEngine } from '@babylonjs/core/Engines/nullEngine';
import { Scene } from '@babylonjs/core/scene';
import type { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { buildTitleBackdrop } from '../../../../src/game/view/title-backdrop';
import { TITLE_LOOK } from '../../../../src/game/config/title-look';

describe('title backdrop', () => {
  let scene: Scene | undefined;
  afterEach(() => {
    scene?.dispose();
    scene = undefined;
  });

  function setup() {
    scene = new Scene(new NullEngine());
    const backdrop = buildTitleBackdrop(scene);
    const node = (name: string) => {
      const found = scene?.getMeshByName(name) ?? scene?.getTransformNodeByName(name);
      if (!found) throw new Error(`no ${name}`);
      return found;
    };
    return { scene, backdrop, node };
  }

  it('P01-R05: generates a sky, a skyline, a city, rain and the balanced ship in code', () => {
    const { scene: s, backdrop, node } = setup();
    for (const name of [
      'title-sky',
      'title-skyline',
      'title-skyline-lights',
      'title-city',
      'title-city-structure',
      'title-city-lights',
      'title-city-lights-2',
      'title-rain',
      'title-ship',
    ]) {
      expect(() => node(name)).not.toThrow();
    }
    expect(node('title-ship').getChildren()).toHaveLength(1);
    expect(node('title-city').getChildren()).toHaveLength(4);
    const lights = s.getMeshByName('title-city-lights')?.material as StandardMaterial;
    expect(lights.emissiveColor.r).toBe(TITLE_LOOK.neonIntensity);
    expect(s.activeCamera?.name).toBe('title-camera');
    expect(s.fogMode).toBe(Scene.FOGMODE_LINEAR);
    expect(backdrop.glowExcludedMeshes.map((m) => m.name)).toEqual([
      'title-sky',
      'title-skyline',
      'title-city-structure',
      'title-city-structure-2',
      'title-rain',
    ]);
  });

  it('P01-R05: the city scrolls at title_city_scroll_speed and loops every chunk', () => {
    const { backdrop, node } = setup();
    const { scrollSpeed, length } = TITLE_LOOK.city;
    backdrop.update(1);
    expect(node('title-city').position.z).toBeCloseTo(-scrollSpeed);
    backdrop.update(length / scrollSpeed - 1);
    expect(node('title-city').position.z).toBeCloseTo(0);
    expect(node('title-city-lights-2').position.z).toBe(length);
  });

  it('P01-R05: the rain falls and loops every rain height', () => {
    const { backdrop, node } = setup();
    const { y, speed, height } = TITLE_LOOK.rain;
    backdrop.update(0.5);
    expect(node('title-rain').position.y).toBeCloseTo(y - speed * 0.5);
    backdrop.update(height / speed - 0.5);
    expect(node('title-rain').position.y).toBeCloseTo(y);
  });

  it('P01-R05: the ship turns at title_ship_rotation_speed and floats', () => {
    const { backdrop, node } = setup();
    const ship = node('title-ship');
    backdrop.update(1);
    expect(ship.rotation.y).toBeCloseTo(0.3);
    expect(ship.position.y).not.toBeCloseTo(TITLE_LOOK.ship.position[1]);
  });

  it('P01-R05 (review): the sky, horizon and buildings are dark, the neon stays bright', () => {
    const { scene: s } = setup();
    const luminance = ([r, g, b]: readonly [number, number, number]) =>
      0.2126 * r + 0.7152 * g + 0.0722 * b;
    expect(luminance([s.clearColor.r, s.clearColor.g, s.clearColor.b])).toBeLessThan(0.1);
    for (const stop of TITLE_LOOK.sky.stops) expect(luminance(stop.color)).toBeLessThan(0.1);
    for (const color of Object.values(TITLE_LOOK.city.colors)) {
      expect(luminance(color)).toBeLessThan(0.1);
    }
    expect(luminance(TITLE_LOOK.skyline.color)).toBeLessThan(0.1);
    for (const color of TITLE_LOOK.city.neonColors) expect(luminance(color)).toBeGreaterThan(0.3);
  });

  it('hides the ship on the ship select screen only', () => {
    const { backdrop, node } = setup();
    backdrop.showScreen('ship-select');
    expect(node('title-ship').isEnabled()).toBe(false);
    backdrop.showScreen('level-select');
    expect(node('title-ship').isEnabled()).toBe(true);
  });
});
