const {
  song_detail,
  song_url,
  lyric,
} = require("../extern/NeteaseCloudMusicApi/main");
async function main() {
  try {
    let result;
    const id = process.argv[2];
    result = await song_url({
      id: +id,
    });
    const url = result.body.data[0].url;

    result = await lyric({
      id: +id,
    });
    lyrics = result.body.lrc.lyric;

    result = await song_detail({
      ids: id,
    });
    result = result.body.songs[0];
    result = {
      title: result.name,
      artists: result.ar.map((ar) => {
        return { name: ar.name, id: ar.id };
      }),
      album: result.al.name,
      album_id: result.al.id,
      cover_url: result.al.picUrl,
      url,
      lyrics,
    };
    console.log(JSON.stringify(result));
  } catch (error) {
    console.log(error);
  }
}
main();
// {"songs":[{"name":"情非得已 (童声版)","id":33894312,"pst":0,"t":0,"ar":[{"id":122455,"name":"群星","tns":[],"alias":[]}],"alia":[],"pop":75,"st":0,"rt":null,"fee":0,"v":714,"crbt":null,"cf":"","al":{"id":3263929,"name":"热门华语275","picUrl":"https://p1.music.126.net/ZDUo6vF_5ykD6E_08HE1kw==/3385396303317256.jpg","tns":[],"pic":3385396303317256},"dt":267232,"h":{"br":320000,"fid":0,"size":10691439,"vd":-2},"m":{"br":192000,"fid":0,"size":6414880,"vd":-2},"l":{"br":128000,"fid":0,"size":4276601,"vd":-2},"a":null,"cd":"1","no":1,"rtUrl":null,"ftype":0,"rtUrls":[],"djId":0,"copyright":2,"s_id":0,"mark":524288,"originCoverType":0,"originSongSimpleData":null,"resourceState":true,"single":0,"noCopyrightRcmd":null,"mst":9,"cp":0,"mv":0,"rtype":0,"rurl":null,"publishTime":1388505600004}],"privileges":[{"id":33894312,"fee":0,"payed":0,"st":0,"pl":320000,"dl":320000,"sp":7,"cp":1,"subp":1,"cs":false,"maxbr":320000,"fl":320000,"toast":false,"flag":0,"preSell":false,"playMaxbr":320000,"downloadMaxbr":320000,"rscl":null,"freeTrialPrivilege":{"resConsumable":false,"userConsumable":false},"chargeInfoList":[{"rate":128000,"chargeUrl":null,"chargeMessage":null,"chargeType":0},{"rate":192000,"chargeUrl":null,"chargeMessage":null,"chargeType":0},{"rate":320000,"chargeUrl":null,"chargeMessage":null,"chargeType":0},{"rate":999000,"chargeUrl":null,"chargeMessage":null,"chargeType":1}]}],"code":200}
