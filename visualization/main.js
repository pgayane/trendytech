var lang_data;
var width = window.innerWidth-100;
var height = window.innerHeight/2;
var lang_data;

var subwidth = window.innerWidth/2;
var subheight = window.innerHeight/2;

var axisPadding = 100;
var barPadding = 1;
var labelPadding = 10;
var barwidth;
var bottomPadding = 120;
var scale;
var prevtime = 0;
var time = 0;

window.onload = function(){

    d3.json('timeline_data.json', function(error, data){
       lang_data = data['languages'];
       multiplyData(lang_data);
       init();
    });

}

function multiplyData(data){

    for (i = 0; i < data.length; i++)
        for (j = 0; j < 6; j++)
            if (data[i]['lang_popularity'][j] != 0)
                data[i]['lang_popularity'][j]  += 2
            
}


function init(){
    
    barwidth = (width - axisPadding)/lang_data.length - barPadding;

    var maxValue = d3.max(lang_data, function(d){
        return d['lang_popularity'][0];
    });
    var mimValue = d3.min(lang_data, function(d){
        return d['lang_popularity'][0];
    });

    scale = d3.scale.linear();
    scale.domain([0, maxValue]);
    scale.range([height - bottomPadding, 0]);

    subscale = d3.scale.linear();
    subscale.range([subheight - bottomPadding, 0]);

    createTimeline();
    displayCurrentTime(time);
    createMainSVG();
    createSubSVG();
    createBars();
    createBarLabels();
};

function createMainSVG(){
    var svg = d3.select('body').append('svg')
                                .attr('id', 'mainsvg')
                                .attr('width', width)
                                .attr('height', height);

    var ys = new Array();
    for(i = 0; i < 7; i++)
    {   
        ys[i] = (i*10 + 2) //Math.pow(2,i*2); //(i*i*10000);
    }
     
    yaxis = d3.svg.axis().scale(scale).orient('left')
                .tickFormat(function(d) { return d-2; })
                .tickValues(ys);
    svg.append('g')
        .attr("transform", "translate(100, 0)")        
        .attr('color', 'green')
        .call(yaxis);

};

function createSubSVG(){
    var svg = d3.select('body').append('svg')
                                .attr('id', 'subsvg')
                                .attr('width', subwidth)
                                .attr('height', subheight);
    

};

function getColor(d, data){
    if (d['name'] == 'other')
        return 'green'
    else
        return 'orange'
    // var data_copy = data.slice();
    // data_copy.sort(function(a,b){return a['lang_popularity'][time]-b['lang_popularity'][time]});

    // if (d['lang_popularity'][time]>= data_copy[data_copy.length*(3/4)]['lang_popularity'][time])
    //     return 'red';
    // else if (d['lang_popularity'][time]>= data_copy[data_copy.length*(2/4)]['lang_popularity'][time])
    //     return 'orange';
    // else if (d['lang_popularity'][time]>= data_copy[data_copy.length*(1/4)]['lang_popularity'][time])
    //     return 'yellow';
    // else
    //     return 'greenyellow';
};

function createBars(){
    var svg = d3.select('#mainsvg');

    var rects = svg.selectAll('rect').data(lang_data);
        rects
        .enter()
        .append('rect')
        .attr('x', function(d, i){return axisPadding + i*(barwidth+barPadding);})
        .attr('y', height - bottomPadding)
        .attr('width', barwidth)
        .attr('height', 0)
        .attr('fill', function(d){ 
            return getColor(d, lang_data)
        })
        .transition()
        .duration(100)
        .attr('height', function(d) { 
           
            return height - bottomPadding - scale(d['lang_popularity'][time]);})
        .attr('y', function(d) { 
            return scale(d['lang_popularity'][time]);} )
        .each('end', function(d, i){
            d3.select(this).call(hoverData);
        });      
};

function updateBarLabels(){
    var svg = d3.select('#mainsvg');
    svg.selectAll('.language')
        .remove();

        createBarLabels();    
};

function createBarLabels(){
    var svg = d3.select('#mainsvg');
    svg.selectAll('.language')
        .data(lang_data)
        .enter()
        .append('text')
        .text(function(d) {
            if (d['lang_popularity'][time] == 0)
                return ''
            else
                return d['name'];
        })
        .attr('x', function(d, i){return axisPadding+ i*(barwidth+barPadding);})
        .attr('y', height-bottomPadding+labelPadding)
        .attr('font.color', 'green')
        .attr('transform', function(d, i) {
            return 'rotate(50 ' + (axisPadding + i*(barwidth+barPadding)).toString() + ' ' + (height-bottomPadding+labelPadding).toString()+")";
        })
        .attr('class', 'language');
}

function highlightBars(selection){
    selection
        .on('mouseover', function(d, i){
            x = this.getAttribute('x');
            y = this.getAttribute('y');

            d3.select(this).attr('fill', '#999');
            d3.select('svg').append('text')
                            .text((d['lang_popularity'][time]-2).toFixed(2) + '%')
                            .attr('id', 'label')
                            .attr('x', x)
                            .attr('y', y)
            createSubBars(d);
        })
        .on('mouseout', function(){
            d3.select(this)
            .attr('fill', function(d){ 
                            return getColor(d, lang_data)
                        });
            d3.select('#label').remove();
        })

};

function createSubAxis(item){
    

    submax = 0
    for(i=0; i < 6; i ++)
        if (submax < item['lang_popularity'][i])
            submax = item['lang_popularity'][i]
    subscale.domain([0, submax]);


    var ys = new Array();
    for(i = 0; i < 5; i++)
    {   
        ys[i] = i*(submax/5)
    }
     
    yaxis = d3.svg.axis().scale(subscale).orient('left')
                .tickFormat(function(d) { return d.toFixed(1); })
                .tickValues(ys);
    d3.select('#subsvg').append('g')
        .attr('id', 'subaxis')
        .attr("transform", "translate(100, 0)")        
        .attr('color', 'green')
        .call(yaxis);
}

function removeSubAxis(){
    d3.select('#subaxis').remove();
}

function createSubBars(item){
    removeSubAxis();
    d3.select('#subsvg').selectAll('rect').remove();

    createSubAxis(item);
    d3.select('#subsvg').selectAll('rect').data(item['lang_popularity'])
                .enter()
                .append('rect')
                .attr('x', function(d, i){return axisPadding + i*(barwidth+barPadding);})
                .attr('y', subheight - bottomPadding)
                .attr('width', barwidth)
                .attr('height', 0)
                .attr('fill', 'green')
                .transition()
                .duration(1000)
                .attr('height', function(d) { return subheight -bottomPadding-subscale(d);})
                .attr('y', function(d) { return  subscale(d);})
};


function hoverData(selection){
    highlightBars(selection);    
};

function updateCurrentTime(time)
{
    d3.select('#year')
        .html(2008 + parseInt(time));
};

function displayCurrentTime(time){
    d3.select('body')
        .append('div')
        .html(2008 + parseInt(time))
        .style('font-size', 30)
        .style('color', 'green')
        .style('float', 'left')
        .attr('id', 'year')
};

function createTimeline(){
    d3.select('body').append('input')
    .attr('type', 'range')
    .attr('min', 0)
    .attr('max', 5)
    .attr('value', 0)
    .attr("name","points")
    .style('float', 'left')
    .on('change', function(){ 
        time = this.value;
        return transform();

    });
    
 };


 function transform(){
    updateCurrentTime(time)
    updateBarLabels();
    updateedRects = d3.select('body').select('#mainsvg').selectAll('rect').data(lang_data);
            
    updateedRects
        .attr('x', function(d, i){return axisPadding + i*(barwidth+barPadding);})
        .attr('width', barwidth)
        .attr('height', function(d) { return height - bottomPadding - scale(d['lang_popularity'][prevtime]);})
        .attr('y', function(d) { return  scale(d['lang_popularity'][prevtime]);} )
        .attr('fill', function(d){ 
            return getColor(d, lang_data)
        })
        .transition()
        .duration(2000)
        .attr('height', function(d) { return height - bottomPadding - scale(d['lang_popularity'][time]);})
        .attr('y', function(d) { return scale(d['lang_popularity'][time]);} )
        .each('end', function(d, i){
                d3.select(this).call(hoverData);  
        })

    prevtime = time;
    
 };