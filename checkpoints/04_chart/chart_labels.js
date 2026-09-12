/* Keep endpoint labels inside the chart without changing the source values. */
(() => {
  const chart = document.querySelector('#chart');
  const align = () => {
    const dots = [...chart.querySelectorAll('circle')];
    dots.forEach((dot, index) => {
      const year = dot.nextElementSibling;
      const value = year?.nextElementSibling;
      for (const label of [year,value]) {
        if (label?.tagName.toLowerCase() !== 'text') continue;
        label.setAttribute('x',dot.getAttribute('cx'));
        label.setAttribute('text-anchor',index === 0 ? 'start' : index === dots.length - 1 ? 'end' : 'middle');
      }
    });
  };
  new MutationObserver(align).observe(chart,{childList:true});
  align();
})();
